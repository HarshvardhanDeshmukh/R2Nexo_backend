r2_app.controller('about_ctrl', function($scope, $http, R2Serv) {

    $scope.students;
    
    $scope.sample = 'asasdad';

    $scope.get_students = function() {
        $http.post('get_student/').then(function(res) {
            R2Serv.handle_fail(res.data.get_student);
            R2Serv.console('response for get_student: ', res);
            $scope.students = res.data.get_all_students.data;
        });
    };

});