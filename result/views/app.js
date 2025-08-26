var app = angular.module('findyourbias', []);
var socket = io.connect();

app.controller('statsCtrl', function($scope, $http){
  $scope.votes = [];
  $scope.total = 0;
  $scope.analysis = null;

  var updateScores = function(){
    socket.on('scores', function (json) {
       $scope.$apply(function () {
         $scope.votes = JSON.parse(json);
         $scope.total = $scope.votes.length;
       });
    });
  };

  $scope.getAnalysis = function() {
    $scope.analysis = "Loading AI analysis...";
    // This will eventually hit your AI microservice endpoint
    // For now, we'll just simulate a delay and a response
    $http.get("http://localhost:5001/analyze").then(function(response) {
        $scope.analysis = response.data;
    }).catch(function() {
        $scope.analysis = "Failed to get analysis. Is the AI service running?";
    });
  };

  var init = function(){
    document.body.style.opacity=1;
    updateScores();
  };
  socket.on('message',function(data){
    init();
  });
});
