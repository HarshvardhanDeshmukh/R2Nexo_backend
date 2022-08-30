r2_app.controller('badgeCtrl', function ($scope, $http, NgTableParams, R2Serv) {
    $scope.sample = 'This is the sample';

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

    $http.post('/admin_view_badges/').then(function (res) {
        if (!R2Serv.handle_fail(res.data.admin_view_badges)) {
            R2Serv.console('response for admin_view_badges is : ', res);
            $scope.badges = res.data.admin_view_badges.badge_list;
            $scope.tableParams = new NgTableParams({}, { dataset: $scope.badges });
        }
    });

    $scope.add_new_badge = function () {
        getBase64($scope.new_badge.image).then(function (converted_image) {
            if (converted_image == 'no image') {
                swal('Error', 'Please select corrent image for the badge!', 'error');
            }
            else {
                $http.post('/admin_add_badge/', JSON.stringify({
                    data: {
                        name: $scope.new_badge.name,
                        desc: $scope.new_badge.desc,
                        image: converted_image
                    }
                })).then(function (res) {
                    if (!R2Serv.handle_fail(res.data.admin_add_badge)) {
                        console.clear();
                        R2Serv.console('response for admin_add_badge: ', res);
                    }
                })
            }
        });
    }

});