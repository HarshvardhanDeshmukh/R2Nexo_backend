r2_app.controller('application_review', function ($scope, $http, $rootScope, NgTableParams, R2Serv) {

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

        var admin_get_topics_req_data = {
            data: {
                "batch_id": $scope.selected_batch.id
            }
        }

        $http.post('/admin_get_topics/', JSON.stringify(admin_get_topics_req_data))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.admin_get_topics)) {
                    R2Serv.console('admin_get_topics response: ', response);

                    $scope.topics = response.data.admin_get_topics.data;
                    if ($scope.topics.length != 0) {
                        $scope.selected_topic = $scope.topics[0]
                        $scope.apps = [];
                        $scope.changed_topic();
                    }
                }
            });
    }

    $scope.changed_topic = function () {

        var admin_get_appls_req_data = {
            data: {
                "topic_id": $scope.selected_topic.topic_id
            }
        }

        $http.post('/admin_get_appls/', JSON.stringify(admin_get_appls_req_data))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.admin_get_appls)) {
                    R2Serv.console('admin_get_appls response: ', response);

                    $scope.apps = response.data.admin_get_appls.data;

                    $scope.tableParams = new NgTableParams({}, { dataset: $scope.apps });
                }
            });
    }

    $scope.save_changes = function () {
        app_to_submit = []

        $scope.apps.forEach(element => {
            app_to_submit.push({
                app_id: element.app_id,
                marks: parseInt(element.app_other_marks),
                student_id: element.student_id
            });
        });

        admin_review_application_req_data = {
            data: {
                app_result: app_to_submit
            }
        }

        $http.post('/admin_review_application/', JSON.stringify(admin_review_application_req_data))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.admin_review_application)) {
                    R2Serv.console('admin_review_application response: ', response);
                    if (response.data.admin_review_application.status == 'success') {
                        swal('Applications review saved successfully!', '', 'success');
                    }
                    else {
                        swal('Something went wrong. Please check your internet connection!', '', 'error');
                    }
                }
            });
    }

});