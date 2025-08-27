using System;
using System.Data.Common;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using Newtonsoft.Json;
using Npgsql;
using StackExchange.Redis;

namespace Worker
{
    public class Program
    {
        public static int Main(string[] args)
        {
            try
            {
                var pgsql = OpenDbConnection("Server=db;Username=postgres;Password=postgres;");
                var redisConn = OpenRedisConnection("redis");
                var redis = redisConn.GetDatabase();

                // Keep alive is not implemented in Npgsql yet. This workaround was recommended:
                // https://github.com/npgsql/npgsql/issues/1214#issuecomment-235828359
                var keepAliveCommand = pgsql.CreateCommand();
                keepAliveCommand.CommandText = "SELECT 1";

                var definition = new { vote = "", voter_id = "", tweet = "", room_id = "" };
                while (true)
                {
                    // Slow down to prevent CPU spike, only query each 100ms
                    Thread.Sleep(100);

                    // Reconnect redis if down
                    if (redisConn == null || !redisConn.IsConnected) {
                        Console.WriteLine("Reconnecting Redis");
                        redisConn = OpenRedisConnection("redis");
                        redis = redisConn.GetDatabase();
                    }
                    string json = redis.ListLeftPopAsync("votes").Result;
                    if (json != null)
                    {
                        var vote = JsonConvert.DeserializeAnonymousType(json, definition);
                        Console.WriteLine($"Processing vote for '{vote.vote}' by '{vote.voter_id}' in room '{vote.room_id}' on tweet '{vote.tweet}'");
                        // Reconnect DB if down
                        if (!pgsql.State.Equals(System.Data.ConnectionState.Open))
                        {
                            Console.WriteLine("Reconnecting DB");
                            pgsql = OpenDbConnection("Server=db;Username=postgres;Password=postgres;");
                        }
                        else
                        {
                            keepAliveCommand.ExecuteNonQuery();
                        }
                        UpdateVote(pgsql, vote.voter_id, vote.vote, vote.tweet, vote.room_id);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex.ToString());
                return 1;
            }
        }

        private static NpgsqlConnection OpenDbConnection(string connectionString)
        {
            NpgsqlConnection connection;

            while (true)
            {
                try
                {
                    connection = new NpgsqlConnection(connectionString);
                    connection.Open();

                    var command = connection.CreateCommand();
                    command.CommandText = @"CREATE TABLE IF NOT EXISTS votes (
                                                id       SERIAL PRIMARY KEY,
                                                vote     VARCHAR(255) NOT NULL,
                                                voter_id VARCHAR(255) NOT NULL,
                                                tweet    VARCHAR(255),
                                                room_id  VARCHAR(50)
                                            );";
                    command.ExecuteNonQuery();

                    break;
                }
                catch (SocketException)
                {
                    Console.Error.WriteLine("Waiting for db");
                    Thread.Sleep(1000);
                }
                catch (DbException)
                {
                    Console.Error.WriteLine("Waiting for db");
                    Thread.Sleep(1000);
                }
            }

            Console.Error.WriteLine("Connected to db");

            return connection;
        }

        private static ConnectionMultiplexer OpenRedisConnection(string hostname)
        {
            // Use IP address to workaround https://github.com/StackExchange/StackExchange.Redis/issues/410
            var ipAddress = GetIp(hostname);
            Console.WriteLine($"Found redis at {ipAddress.ToString()}");

            while (true)
            {
                try
                {
                    Console.Error.WriteLine("Connecting to redis");
                    return ConnectionMultiplexer.Connect(ipAddress.ToString());
                }
                catch (RedisConnectionException)
                {
                    Console.Error.WriteLine("Waiting for redis");
                    Thread.Sleep(1000);
                }
            }
        }

        private static IPAddress GetIp(string hostname)
            => Dns.GetHostEntryAsync(hostname)
                .Result
                .AddressList
                .First(a => a.AddressFamily == AddressFamily.InterNetwork);

        private static void UpdateVote(NpgsqlConnection connection, string voterId, string vote, string tweet, string roomId)
        {
            var command = connection.CreateCommand();
            try
            {
                // First, try to update an existing vote
                command.CommandText = "UPDATE votes SET vote = @vote, tweet = @tweet, room_id = @roomId WHERE voter_id = @voterId";
                command.Parameters.AddWithValue("@voterId", voterId);
                command.Parameters.AddWithValue("@vote", vote);
                command.Parameters.AddWithValue("@tweet", tweet);
                command.Parameters.AddWithValue("@roomId", roomId);
                var rows = command.ExecuteNonQuery();

                // If no rows were updated, it means the voter_id doesn't exist, so insert a new one
                if (rows == 0)
                {
                    command.CommandText = "INSERT INTO votes (voter_id, vote, tweet, room_id) VALUES (@voterId, @vote, @tweet, @roomId)";
                    command.ExecuteNonQuery();
                }
            }
            catch (DbException ex)
            {
                Console.Error.WriteLine($"Error updating/inserting vote: {ex.Message}");
            }
            finally
            {
                command.Dispose();
            }
        }
    }
}