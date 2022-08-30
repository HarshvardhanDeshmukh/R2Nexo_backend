r2_app.controller('new_quiz_ctrl', function($scope, $http, $rootScope, R2Serv) {
    $scope.questions = [];
    
    $scope.populate_batches = function() {
        
        var get_all_batches_req_data = {};

        $http.post("/get_all_batches/", JSON.stringify(get_all_batches_req_data), JSON.stringify($rootScope.post_config))
        .then(function(response) {
            if (!R2Serv.handle_fail(response.data.get_all_batches)) {
                R2Serv.console('get_all_batches : ', response);
                $scope.batches = response.data.get_all_batches.data;
                $scope.batches_result = response.data.get_all_batches.message;
                $scope.selected_batch = $scope.batches[0];
                R2Serv.console('$scope.batches: ', $scope.batches);
                $http.post('/get_quiz_quest_to_choose/').then(function(res) {
                    if (!R2Serv.handle_fail(res.data.get_quiz_quest_to_choose)){
                        $scope.quiz_list = res.data.get_quiz_quest_to_choose.data;
                        R2Serv.console('response for get_quiz_quest_to_choose: ', $scope.quiz_list);
                    }
                });
            }
        }, function(err){
            R2Serv.console('error in requesting all_batches', err);
        });
    }

    $scope.populate_batches();
    
    $scope.add_question = function() {
        $scope.questions.push({
            title: "This is the question",
            type: "Essay",
            option_a: "",
            option_b: "",
            option_c: "",
            option_d: "",
            correct_ans: "A"
        });
    }

    $scope.delete_question = function(question_to_del) {

        q_index = $scope.questions.indexOf(question_to_del);

        if (confirm('Delete this Question? you wont be able to revert the changes!')) {
            if (q_index > -1)
                $scope.questions.splice(q_index, 1);
        }
    }

    $scope.publish_quiz = function() {

        var blank_options  = {
            value: false,
            question: ''
        }

        var is_question_large = false;
        
        $scope.questions.forEach(element => {
            if (element.type == 'MCQ') {
                if ($rootScope.is_blank(element.option_a) || $rootScope.is_blank(element.option_b) || $rootScope.is_blank(element.option_c) || $rootScope.is_blank(element.option_d)) {
                    blank_options.value = true;
                    blank_options.question = element.title;
                    // swal('Please provide answer for the question: ' + element.title);
                }
            }

        });

        if (is_question_large) {
            swal('Question is too big!', 'Please make sure the question is within 150 characters', 'warning');
        }
        else if ($rootScope.is_blank($scope.quiz_desc)) {
            swal('Please provide Quiz Description!', '', 'warning');
        }
        else if ($scope.questions.length == 0){
            swal('No questions added in this quiz!', '', 'warning');
        }
        else if(blank_options.value) {
            swal('Please provide answer for the question: ' + blank_options.question);
        }
        else {
            swal({
                title: 'Publish quiz?',
                showCancelButton: true,
                confirmButtonColor: '#4fa7f3',
                cancelButtonColor: '#d57171',
                confirmButtonText: 'Yes, publish now!'
            }).then(function () {

                var create_quiz_req_data = {
                    data: {
                        data: {
                            batch_id: $scope.selected_batch.id,
                            desc: $scope.quiz_desc,
                            questions: $scope.questions
                        }
                    }
                };

                R2Serv.console('\n\n\n\n\n\n FINAL REQ: ', create_quiz_req_data.data);

                $http.post('/create_quiz/', JSON.stringify(create_quiz_req_data), JSON.stringify($rootScope.post_config))
                .then(function(response) {
                    if (!R2Serv.handle_fail(response.data.create_quiz)) {
                        R2Serv.console('\n\n\n create_quiz response: ', response);
                        
                        swal('Quiz published', '', 'info').then(function() {
                            // location.reload();
                        });
                    }
                });
            })
        }
    }

    $scope.select_quiz = function() {
        $scope.questions = angular.copy($scope.selected_quiz.questions);
    }

});