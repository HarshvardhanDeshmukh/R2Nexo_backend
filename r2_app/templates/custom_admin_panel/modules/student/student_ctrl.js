r2_app.controller('student_ctrl', function ($scope, $http, NgTableParams, $rootScope, $timeout, R2Serv) {

    $scope.show_loader = true;

    $scope.populate_batches = function () {

        var get_all_batches_req_data = {};

        $http.post("/get_all_batches/", JSON.stringify(get_all_batches_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_all_batches)) {
                    R2Serv.console('get_all_batches : ', response);
                    $scope.batches = response.data.get_all_batches.data;
                    $scope.new_student.batch = $scope.batches[0];
                    R2Serv.console('$scope.batches: ', $scope.batches);
                }
            }, function (err) {
                R2Serv.console('error in requesting all_batches', err);
            });
    }

    $scope.populate_batches();

    $scope.new_student = {
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        batch: {}
    };

    function getBase64(file) {

        return new Promise(function (resolve, reject) {
            if (typeof file === 'undefined' || file == null) {
                resolve('no image');
            }
            else {
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function () {
                    var newImage = reader.result.toString().split(",");
                    resolve(newImage[1]);
                };
                reader.onerror = function (error) {
                    R2Serv.console('Error in getBase64: ', error);
                    reject(error);
                };
            }
        });
    }

    $scope.populate_students = function () {

        var get_students_req_data = {};

        $http.post("/get_students/", JSON.stringify(get_students_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_students)) {
                    $scope.show_loader = false;
                    R2Serv.console('get_students : ', response);
                    $scope.students = response.data.get_students.data;

                    R2Serv.console('$scope.students: ', $scope.students);

                    $scope.tableParams = new NgTableParams({}, { dataset: $scope.students });
                }
            }, function (err) {
                R2Serv.console('error in requesting get_students', err);
            });
    }

    $scope.populate_students();

    $scope.edit_student = function (student_to_edit) {
        $scope.current_student = student_to_edit;
        $scope.current_student.new_profile_pic = null;

        $scope.current_student_index = $scope.students.indexOf(student_to_edit);

        $scope.batches.forEach(element => {
            if (element.id == $scope.current_student.batch_id) {
                $scope.selected_batch = element;
            }
        });
    }

    $scope.prepareBadgeUpdate = function (student_to_edit) {
        $scope.current_student = student_to_edit;
    }

    $scope.save_edit = function () {
        if ($rootScope.is_blank($scope.current_student.first_name)) {
            swal('First name needed!', 'Please provide first name of the student.', 'error');
        }
        else if ($rootScope.is_blank($scope.current_student.last_name)) {
            swal('Last name needed!', 'Please provide last name of the student.', 'error');
        }
        else if ($rootScope.is_blank($scope.current_student.password)) {
            swal('Password needed!', 'Please provide password for the student.', 'error');
        }
        else {
            getBase64($scope.current_student.new_profile_pic)
                .then(function (new_image) {
                    var edit_student_req_data = {
                        data: {
                            id: $scope.current_student.id,
                            email: $scope.current_student.email,
                            first_name: $scope.current_student.first_name,
                            last_name: $scope.current_student.last_name,
                            batch_id: $scope.selected_batch.id,
                            device_type: $scope.current_student.device,
                            os_version: $scope.current_student.os_version,
                            app_version: $scope.current_student.app_version,
                            password: $scope.current_student.password,
                            profile_pic: new_image
                        }
                    };
                    $http.post("/edit_student/", JSON.stringify(edit_student_req_data), JSON.stringify($rootScope.post_config))
                        .then(function (response) {
                            if (!R2Serv.handle_fail(response.data.edit_student)) {
                                // $scope.students[$scope.current_student_index].picture_url = 'student_profile_picture/'+$scope.students[$scope.current_student_index].id+'/image.png';
                                swal('Student updates successfully!');
                                $scope.current_student.full_name = $scope.current_student.first_name + ' ' + $scope.current_student.last_name;
                                R2Serv.console('\n edit_student success response: ', response);
                            }
                        }, function (err) {
                            console.error('\n edit_student fail response: ', err);
                        });
                });
        }
    }

    $scope.delete_student = function (student_to_delete) {
        swal({
            title: 'Delete ' + student_to_delete.first_name + '?',
            text: "You won't be able to revert this!",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4fa7f3',
            cancelButtonColor: '#d57171',
            confirmButtonText: 'Yes, delete ' + student_to_delete.first_name + '!'
        }).then(function () {

            var delete_student_req_data = {
                data: {
                    email: student_to_delete.email
                }
            };

            $http.post('/delete_student/', JSON.stringify(delete_student_req_data), JSON.stringify($rootScope.post_config))
                .then(function (response) {
                    if (!R2Serv.handle_fail(response.data.delete_student)) {
                        R2Serv.console('\n delete_student response: ', response);
                        var index_to_delete = $scope.batches.indexOf(student_to_delete)
                        if (index_to_delete > -1) {
                            $scope.batches.splice(index_to_delete, 1);
                        }
                        swal('Deleted!', 'Student has been deleted.', 'success').then(function () {
                            location.reload();
                        });
                    }
                });
        })
    }

    $scope.add_new_student = function () {

        if ($rootScope.is_blank($scope.new_student.first_name)) {
            swal('First name needed!', 'Please provide first name of the student.', 'error');
        }
        else if ($rootScope.is_blank($scope.new_student.last_name)) {
            swal('Last name needed!', 'Please provide last name of the student.', 'error');
        }
        else if ($rootScope.is_blank($scope.new_student.email)) {
            swal('Email needed!', 'Please provide email of the student.', 'error');
        }
        else if ($rootScope.is_blank($scope.new_student.password)) {
            swal('Password needed!', 'Please provide password of the student.', 'error');
        }
        else {
            getBase64($scope.new_student.new_profile_pic)
                .then(function (converted_image) {
                    var add_student_req_data = {
                        data: {
                            email: $scope.new_student.email,
                            first_name: $scope.new_student.first_name,
                            last_name: $scope.new_student.last_name,
                            password: $scope.new_student.password,
                            profile_pic: converted_image,
                            batch_id: $scope.new_student.batch.id
                        }
                    };
                    $http.post('/add_student/', JSON.stringify(add_student_req_data), JSON.stringify($rootScope.post_config))
                        .then(function (response) {
                            R2Serv.console('add_student response: ', response);
                            if (response.data.add_student.status == 'success') {
                                $rootScope.student_count += 1;
                                swal('Student added successfuly', '', 'success')
                                    .then(function () {
                                        location.reload();
                                    });
                            }
                            else {
                                if (response.data.add_student.message == 'Error in add_student API: This student already exists') {
                                    swal('Student already exist with email address:\n' + $scope.new_student.email, '', 'warning');
                                }
                                else {
                                    swal('Something went wrong, please contact administrator', '', 'warning');
                                }
                            }
                        });
                }).catch(function (errorr) {
                    R2Serv.console('\n\n\n\n Converted Image ERROR: \n\n\n\: ', errorr);
                });
        }
    }

    $scope.updateStudentBadge = function () {
        $http.post('/update_student_badges/', JSON.stringify({
            data: {
                student_id: $scope.current_student.id,
                badge_list: $scope.current_student.badge_list
            }
        })).then(function (res) {
            if (!R2Serv.handle_fail(res.data.update_student_badges)) {
                console.clear();
                // R2Serv.console('resoponse for update_student_badges: ', res.data.update_student_badges.status);
                R2Serv.console('resoponse for update_student_badges', res.data.update_student_badges.status);
                swal('Done!', 'Student badge updated successfully!', 'success');
            }
        })
    }

});