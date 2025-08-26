var app = angular.module('findyourbias', []);
var socket = io.connect();

app.controller('statsCtrl', function($scope, $http){
  $scope.votes = [];
  $scope.total = 0;
  $scope.analysis = null;
  $scope.room_id = new URLSearchParams(window.location.search).get('room_id');

  var updateScores = function(){
    socket.on('scores', function (json) {
       $scope.$apply(function () {
         $scope.votes = JSON.parse(json);
         $scope.total = $scope.votes.length;
       });
    });
  };

  $scope.getAnalysis = function() {
    if (!$scope.room_id) {
        $scope.analysis = "No room specified. Please join a room to get an analysis.";
        return;
    }
    $scope.analysis = "Loading AI analysis...";
    var host = window.location.hostname;
    var url = "http://" + host + ":31002/analyze?room_id=" + $scope.room_id;
    
    $http.get(url).then(function(response) {
        $scope.analysis = response.data.analysis;
    }).catch(function() {
        $scope.analysis = "Failed to get analysis. Is the AI service running at " + url + "?";
    });
  };

  var init = function(){
    document.body.style.opacity=1;
    if ($scope.room_id) {
        socket.emit('subscribe', { channel: $scope.room_id });
        updateScores();
    }
  };
  socket.on('message',function(data){
    init();
  });
});
