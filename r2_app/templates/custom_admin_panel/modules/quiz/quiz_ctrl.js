r2_app.controller('quiz_ctrl', function ($scope, $http, $rootScope, R2Serv) {

    $scope.current_question_index = 0;


    $scope.get_batch_list = function () {

        var get_all_batches_req_data = {};

        $http.post("/get_all_batches/", JSON.stringify(get_all_batches_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_all_batches)) {
                    R2Serv.console('response for get_all_batches : ', response);
                    $scope.batches = response.data.get_all_batches.data;
                    $scope.batches_result = response.data.get_all_batches.message;
                    $scope.selected_batch = $scope.batches[0];

                    $scope.changed_batch();
                }

            }, function (err) {
                R2Serv.console('error in requesting all_batches', err);
            });
    }

    $scope.get_batch_list();

    $scope.changed_batch = function () {

        var get_quiz_by_batch_admin_req_data = {
            data: {
                batch_id: $scope.selected_batch.id
            }
        };

        $http.post("/get_quiz_by_batch_admin/", JSON.stringify(get_quiz_by_batch_admin_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_quiz_by_batch_admin)) {
                    R2Serv.console('response for get_quiz_by_batch_admin : ', response);
                    $scope.quizzes = response.data.get_quiz_by_batch_admin.data;
                    $scope.quizzes_result = response.data.get_quiz_by_batch_admin.message;
                    if ($scope.quizzes.length != 0) {
                        $scope.selected_quiz = $scope.quizzes[0];
                        $scope.changed_quiz();
                    }
                }
            }, function (err) {
                R2Serv.console('error in requesting all_quizzes', err);
            });


    }

    $scope.changed_quiz = function () {

        $scope.current_question_index = 0;

        R2Serv.console('Quiz changed!', $scope.selected_quiz);

        var get_question_by_quiz_admin_req_data = {
            data: {
                quiz_id: $scope.selected_quiz.quiz_id + ''
            }
        };

        $http.post("/get_question_by_quiz_admin/", JSON.stringify(get_question_by_quiz_admin_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_question_by_quiz_admin)) {
                    R2Serv.console('get_question_by_quiz_admin : ', response);
                    $scope.questions = response.data.get_question_by_quiz_admin.questions;

                    R2Serv.console('$scope.quizzes: ', $scope.quizzes);
                }
            }, function (err) {
                R2Serv.console('error in requesting all_quizzes', err);
            });
    }

    $scope.previous_question = function () {
        if ($scope.current_question_index > 0) {
            $scope.current_question_index -= 1;
        }
    }

    $scope.next_question = function () {
        if ($scope.current_question_index < $scope.questions.length - 1) {
            $scope.current_question_index += 1;
        }
    }

    $scope.change_marks = function (selected_answer_index) {
        R2Serv.console('\n\n\nnew marks: ', selected_answer_index);
        $scope.questions[$scope.current_question_index].answers[selected_answer_index].answer_status = 'Checked'
    }

    $scope.submit_quiz_review = function (final_review) {



        var submit_quiz_review_req_data = {
            data: {
                answers: final_review
            }
        };

        R2Serv.console('\n\n\nFinal Review: ', final_review);

        $http.post('/submit_quiz_review/', JSON.stringify(submit_quiz_review_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.submit_quiz_review)) {
                    R2Serv.console('\n\nsubmit_quiz_review: ', response);
                    swal('Answers reviewed successfully!');
                    $scope.next_question();
                }
            });
    }

});