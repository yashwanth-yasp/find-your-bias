var app = angular.module('findyourbias', []);
var socket = io.connect({ path: '/result/socket.io/' });

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
    var url = "/result/api/analyze";
    
    $http.get(url).then(function(response) {
        $scope.analysis = response.data.analysis;
    }).catch(function(error) {
        console.error("Error fetching analysis:", error);
        $scope.analysis = "Failed to get analysis. Could not reach the backend.";
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
