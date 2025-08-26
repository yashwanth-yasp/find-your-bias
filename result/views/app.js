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
    var host = window.location.hostname;
    var url = "http://" + host + ":31002";
    
    $http.get(url).then(function(response) {
        $scope.analysis = response.data.analysis;
    }).catch(function() {
        $scope.analysis = "Failed to get analysis. Is the AI service running at " + url + "?";
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
