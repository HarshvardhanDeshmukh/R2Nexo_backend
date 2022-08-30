r2_app.controller('post_ctrl', function ($scope, $sce, $http, NgTableParams, $rootScope, $timeout, R2Serv) {

    R2Serv.console('\nloaded post_ctrl.js');

    $scope.ckEditorOptions = $rootScope.ckEditorOptions;
    // $scope.diableCkEditorOptions = $rootScope.diableCkEditorOptions;

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
                    R2Serv.console('Error: ', error);
                    reject(error);
                };
            }
        });
    }

    $scope.get_embed_code = function (_url) {
        embed_code = '';
        _url_arr = _url.split('/');
        embed_code = _url_arr[_url_arr.length];
        return embed_code;
    }

    $scope.new_post = {
        text: '',
        title: '',
        batch: []
    };

    $scope.populate_batches = function () {

        var get_all_batches_req_data = {};

        $http.post("/get_all_batches/", JSON.stringify(get_all_batches_req_data), JSON.stringify($rootScope.post_config))
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.get_all_batches)) {
                    R2Serv.console('get_all_batches : ', response);
                    $scope.batches = response.data.get_all_batches.data;
                    R2Serv.console('post_ctrl::: $scope.batches: ', $scope.batches);
                }
            }, function (err) {
                R2Serv.console('error in requesting all_batches', err);
            });
    }
    $scope.populate_batches();

    $scope.show_loader = true;

    $scope.populate_posts = function () {

        $http.post("/admin_get_posts/")
            .then(function (response) {
                if (!R2Serv.handle_fail(response.data.admin_get_posts)) {
                    R2Serv.console('admin_get_posts : ', response);
                    $scope.posts = response.data.admin_get_posts.data;
                    $scope.tableParams = new NgTableParams({}, { dataset: $scope.posts });
                    R2Serv.console('$scope.posts: ', $scope.posts);
                    $scope.show_loader = false;
                }
            }, function (err) {
                R2Serv.console('error in requesting admin_get_posts', err);
            });
    }

    $scope.populate_posts();

    $scope.edit_post = function (post_to_edit) {
        $scope.current_post = post_to_edit;
        // $scope.current_post.img_url = null;

        $scope.current_post_index = $scope.posts.indexOf(post_to_edit);

        $scope.batches.forEach(element => {
            if (element.id == $scope.current_post.batch_id) {
                $scope.selected_batch = element;
            }
        });
    }

    $scope.save_edit = function () {

        var local_vdo_url = '';

        if ($rootScope.is_blank($scope.current_post.video_url) || $scope.current_post.video_url == 'None')
            local_vdo_url = 'no video';

        if ($rootScope.is_blank($scope.current_post.title)) {
            swal('Title is needed!', 'Please provide title of the post.', 'error');
        }
        else if ($rootScope.is_blank($scope.current_post.text)) {
            swal('Content is needed!', 'Please provide content of the post.', 'error');
        }
        else {
            getBase64($scope.current_post.new_img_url)
                .then(function (new_image) {
                    var admin_udpate_post_req_data = {
                        data: {
                            post_id: $scope.current_post.post_id,
                            post_title: $scope.current_post.title,
                            post_text: $scope.current_post.text,
                            video_url: local_vdo_url,
                            img_url: new_image
                        }
                    };
                    $http.post("/admin_udpate_post/", JSON.stringify(admin_udpate_post_req_data), JSON.stringify($rootScope.post_config))
                        .then(function (response) {
                            if (!R2Serv.handle_fail(response.data.admin_udpate_post)) {
                                swal('Post updates successfully!');
                                R2Serv.console('\n admin_udpate_post success response: ', response);
                            }
                        }, function (err) {
                            console.error('\n admin_udpate_post fail response: ', err);
                        });
                });
        }
    }

    $scope.delete_post = function (post_to_delete) {
        swal({
            title: 'Delete this post?',
            text: "You won't be able to revert this!",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4fa7f3',
            cancelButtonColor: '#d57171',
            confirmButtonText: 'Yes, delete this post!'
        }).then(function () {

            var delete_post_req_data = {
                data: {
                    post_id: post_to_delete.post_id
                }
            };

            $http.post('/admin_delete_post/', JSON.stringify(delete_post_req_data), JSON.stringify($rootScope.post_config))
                .then(function (response) {
                    if (!R2Serv.handle_fail(response.data.admin_delete_post)) {
                        R2Serv.console('\n delete_post response: ', response);
                        var index_to_delete = $scope.batches.indexOf(post_to_delete)
                        if (index_to_delete > -1) {
                            $scope.batches.splice(index_to_delete, 1);
                        }
                        swal('Deleted!', 'Post has been deleted.', 'success').then(function () {
                            location.reload();
                        });
                    }
                });
        })
    }

    $scope.add_new_post = function () {

        $scope.show_loader = true;

        if ($rootScope.is_blank($scope.new_post.title)) {
            swal('Title required', 'Please provide title for the Post', 'error');
        }
        else if ($rootScope.is_blank($scope.new_post.text)) {
            swal('Content required', 'Please provide content for the Post', 'error');
        }
        else if ($scope.new_post.batch.length == 0) {
            swal('Batch required', 'Please select at least one batch', 'error');
        }
        else {
            getBase64($scope.new_post.new_image)
                .then(function (converted_image) {

                    __video_url = '';

                    var __has_video = !$rootScope.is_blank($scope.new_post.video_url);

                    if (__has_video) {
                        __video_url = $scope.new_post.video_url;
                    }
                    else {
                        __video_url = null;
                    }

                    R2Serv.console('\n\n\n has video URL: ', __has_video);

                    add_new_post_req_data = {
                        data: {
                            text: $scope.new_post.text,
                            title: $scope.new_post.title,
                            batches: $scope.new_post.batch,
                            has_img: converted_image != 'no image',
                            image: converted_image,
                            video_url: __video_url,
                            has_video: __has_video
                        }
                    }

                    $http.post('/admin_add_post/', JSON.stringify(add_new_post_req_data))
                        .then(function (response) {
                            if (!R2Serv.handle_fail(response.data.admin_add_post)) {
                                R2Serv.console('\n\n\nadmin_add_post response: ', response);
                                swal('Post added successfully!', '', 'success')
                                    .then(function () {
                                        $scope.show_loader = false;
                                        location.reload();
                                        $scope.new_post = {
                                            text: '',
                                            title: '',
                                            batch: []
                                        };
                                    });
                            }
                        });

                });
        }
    }

    $scope.change_select_all_batch = function () {
        if ($scope.select_all_batches) {
            $scope.new_post.batch = $scope.batches;
        }
        else {
            $scope.new_post.batch = [];
        }
    }

});