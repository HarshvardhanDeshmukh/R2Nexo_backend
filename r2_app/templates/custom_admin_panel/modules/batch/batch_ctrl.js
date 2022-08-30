r2_app.controller('batch_ctrl', function ($scope, $http, NgTableParams, $rootScope, R2Serv) {

    R2Serv.console('$rootScope.post_config', $rootScope.post_config);

    // $scope.batch_table_is_ready = false;

    // $scope.batches = [
    //     {company_name: "loading...", desc: 'loading...', create_at: 'loading...', age: 50}
    // ];
    // $scope.tableParams = new NgTableParams({}, { dataset: $scope.batches});

    $scope.new_batch = {
        company_name: '',
        desc: ''
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
                    // R2Serv.console('newImage: ', newImage[1]);
                    resolve(newImage[1]);
                    // R2Serv.console(reader.result);
                };
                reader.onerror = function (error) {
                    R2Serv.console('Error: ', error);
                    reject(error);
                };
            }
        });
    }

    R2Serv.console('\nloaded batch_ctrl.js');

    // var $rootScope.post_config = {
    //     headers: {
    //         "content-type": "application/x-www-form-urlencoded"
    //     }
    // };

    $scope.populate_batches = function () {

        var get_all_batches_req_data = {};

        $http.post("/get_all_batches/", JSON.stringify(get_all_batches_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_all_batches)) {
                    R2Serv.console('get_all_batches : ', response);
                    $scope.batches = response.data.get_all_batches.data;
                    $scope.batches_result = response.data.get_all_batches.message;

                    R2Serv.console('$scope.batches: ', $scope.batches);
                    // $('.r2_datatable').DataTable();
                    $scope.tableParams = new NgTableParams({}, { dataset: $scope.batches });
                    // $scope.batch_table_is_ready = true;
                }
            }, function (err) {
                R2Serv.console('error in requesting get_all_batches', err);
            });
    }

    $scope.populate_batches();

    $scope.edit_batch = function (current_batch_res) {
        $scope.current_batch = current_batch_res;
        $scope.current_batch.new_logo = null;
    }

    $scope.save_edit = function () {
        if ($scope.current_batch.company_name.trim() == '') {
            swal('Company name needed!', 'Please provide name of the company.', 'error');
        }
        else if ($scope.current_batch.desc.trim() == '') {
            swal('Company description needed!', 'Please provide description of the company.', 'error');
        }
        else {
            getBase64($scope.current_batch.new_logo)
                .then(function (new_image) {
                    var update_batch_req_data = {
                        data: {
                            batch_desc: $scope.current_batch.desc,
                            company_name: $scope.current_batch.company_name,
                            batch_id: $scope.current_batch.id,
                            batch_name: $scope.current_batch.batch_name,
                            company_logo: new_image
                        }
                    };
                    $http.post("/update_batch/", JSON.stringify(update_batch_req_data), JSON.stringify($rootScope.post_config))
                        .then(function (response) {
                            if (!R2Serv.handle_fail(response.data.update_batch)) {
                                swal('Batch updates successfully!');
                                $scope.current_batch.company_logo = response.data.update_batch.new_logo;
                                R2Serv.console('\n update_batch success response: ', response);
                            }
                        }, function (err) {
                            console.error('\n update_batch fail response: ', err);
                        });
                });
        }
    }

    $scope.delete_batch = function (batch_to_delete) {
        swal({
            title: 'Delete ' + batch_to_delete.company_name + '?',
            text: "Everything related to this batch, including students, quizzes, assignments, applications and other things will be deleted!",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4fa7f3',
            cancelButtonColor: '#d57171',
            confirmButtonText: 'Yes, delete it!'
        }).then(function () {

            var delete_batch_req_data = {
                data: {
                    batch_id: batch_to_delete.id
                }
            };

            $http.post('/delete_batch/', JSON.stringify(delete_batch_req_data), JSON.stringify($rootScope.post_config))
                .then(function (response) {
                    if (!R2Serv.handle_fail(response.data.delete_batch)) {
                        R2Serv.console('\n delete_batch response: ', response);
                        var index_to_delete = $scope.batches.indexOf(batch_to_delete)
                        if (index_to_delete > -1) {
                            $scope.batches.splice(index_to_delete, 1);
                        }
                        swal('Deleted!', 'Batch has been deleted.', 'success').then(function () {
                            location.reload();
                        });
                    }
                });
        })
    }

    $scope.add_new_batch = function () {
        if ($scope.new_batch.company_name.trim() == '') {
            swal('Company name needed!', 'Please provide name of the company.', 'error');
        }
        else if ($scope.new_batch.desc.trim() == '') {
            swal('Company description needed!', 'Please provide description of the company.', 'error');
        }
        else {
            getBase64($scope.new_batch.company_logo)
                .then(function (converted_image) {
                    if (converted_image == 'no image') {
                        swal('Oops.. Unable to add batch', 'Please choose company logo and try again', 'error');
                    }
                    else {
                        var add_batch_req_data = {
                            data: {
                                batch_desc: $scope.new_batch.desc,
                                company_name: $scope.new_batch.company_name,
                                batch_name: $scope.new_batch.batch_name,
                                company_logo: converted_image
                            }
                        };
                        // R2Serv.console('\n\n\n\n Converted Image: \n\n\n\: ', converted_image);
                        $http.post('/add_batch/', JSON.stringify(add_batch_req_data), JSON.stringify($rootScope.post_config))
                            .then(function (response) {
                                if (!R2Serv.handle_fail(response.data.add_batch)) {
                                    R2Serv.console('add_batch response: ', response);
                                    $scope.batches = null;
                                    $scope.populate_batches();
                                    $rootScope.batch_count += 1;
                                    swal('Batches added successfuly', '', 'success');
                                }
                            });
                    }
                }).catch(function (errorr) {
                    R2Serv.console('\n\n\n\n Converted Image ERROR: \n\n\n\: ', errorr);
                });
        }
    }

    $("th div input").attr('placeholder', '');

});