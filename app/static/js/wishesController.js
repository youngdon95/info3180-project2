angular.module('WishList').controller('WishesController',['$scope','$http','$log','$window','$location','$cookies','$uibModal','APIService',function($scope,$location,$http,$log,$window,$cookies,$uibModal,APIService){
    $scope.currentUserName = $cookies.get('userName');
    $scope.currentUserId = $cookies.get('userId');
    var wishes;
    var userid=$cookies.get('userId');
    if($cookies.get('loggedIn')!='true'){
        console.log("invalid access");
        $location.path('/');
    }
    
    APIService.getWishes($scope.currentUserId)
    .then(function(data){
        $scope.wishes = data.data.wishes;
        wishes = $scope.wishes;
    })
    .catch(function(){
        
    });
    
    $scope.shareWishlist = function(){
        var modalInstance = $uibModal.open({
            templateUrl : 'static/templates/sharewishes.html',
            controller : 'ShareModal',
            size: 'md',
            animation: true,
            resolve: {
                user : function(){
                    return $scope.currentUserId;
                },
                wishes : function(){
                    return wishes;
                }
            }
        });
        modalInstance.result.then(function(data){
            APIService.sendWishes(data.emails,data.subject,data.message,data.wishes,data.user)
            .then(function(){
                $location.path('/wishes');
            });
        });
    };
    $scope.delete = function() {
   
      $http.post('/api/user/'+ userid +'/wishlist/delete/' + this.wish.id)
      .success(function(data) {
        if (data.message == 'Success') {
        $window.location.reload();
      }else if(data.message == 'Failed'){
        $log.log(data);
      }
      })
     .error(function(error) {
         $log.log(error);
      })
   };

}]);

angular.module('WishList').controller('ShareModal',function($scope,$uibModalInstance,user,wishes){

    $scope.confirm = function(){
        var emails = $scope.emails.split(',');
        var wishtitles = [];
        for(var wish=0; wish<wishes.length;wish++){
            wishtitles.push(wishes[wish].title);
        }
        var result = ({"user":user,"emails":emails,"subject":$scope.subject,"message":$scope.message,"wishes":wishtitles});
        $uibModalInstance.close(result);
    };
    
    $scope.cancel= function (){
        $uibModalInstance.dismiss();
    };
});