r2_app.controller('review_as_ctrl', function ($scope, $http, $rootScope, R2Serv) {

    $scope.current_ass_index = 0;

    $scope.ckEditorOptions = $rootScope.ckEditorOptions;

    $scope.get_batch_list = function () {

        var get_all_batches_req_data = {};

        $http.post("/get_all_batches/", JSON.stringify(get_all_batches_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_all_batches)) {
                    R2Serv.console('get_all_batches : ', response);
                    $scope.batches = response.data.get_all_batches.data;
                    $scope.batches_result = response.data.get_all_batches.message;
                    $scope.selected_batch = $scope.batches[0];

                    $scope.changed_batch();

                    R2Serv.console('$scope.batches: ', $scope.batches);
                }
            }, function (err) {
                R2Serv.console('error in requesting all_batches', err);
            });
    }

    $scope.get_batch_list();

    $scope.changed_batch = function () {
        R2Serv.console('\n\nbatch is changed: ', $scope.selected_batch);

        var admin_get_assign_ans_req_data = {
            data: {
                batch_id: $scope.selected_batch.id
            }
        };

        $http.post("/admin_get_assign_ans/", JSON.stringify(admin_get_assign_ans_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.admin_get_assign_ans)) {
                    R2Serv.console('response for admin_get_assign_ans : ', response);
                    $scope.current_ass_index = 0;
                    $scope.assignments = response.data.admin_get_assign_ans.data;
                    $scope.assignments_result = response.data.admin_get_assign_ans.message;
                    if ($scope.assignments.length != 0) {
                        $scope.selected_assignment = $scope.assignments[0];
                    }
                }
            }, function (err) {
                R2Serv.console('error in requesting all_assignments', err);
            });


    }

    $scope.previous_assign = function () {
        if ($scope.current_ass_index > 0) {
            $scope.current_ass_index -= 1;
            $scope.selected_assignment = $scope.assignments[$scope.current_ass_index]
        }
    }

    $scope.next_assign = function () {
        if ($scope.current_ass_index < $scope.assignments.length - 1) {
            $scope.current_ass_index += 1;
            $scope.selected_assignment = $scope.assignments[$scope.current_ass_index]
        }
    }

    $scope.submit_review = function () {

        ans = []

        $scope.selected_assignment.ass_ans.forEach(element => {
            ans.push({
                marks: element.student_marks,
                ans_id: element.ans_id,
                student_id: element.student_id
            })
        });

        admin_review_assign_req_data = {
            data: {
                ans: ans
            }
        }

        $http.post('/admin_review_assign/', JSON.stringify(admin_review_assign_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.admin_review_assign)) {
                    R2Serv.console('response for admin_review_assign', response);
                    swal('Review submitted successfully!', '', 'success');
                }
            });
    }

});