var r2_app = angular.module('r2_app', ['ui.router', 'ngTable', 'ngCkeditor']);

r2_app.config(function($httpProvider, $interpolateProvider, $stateProvider, $urlRouterProvider, ) {
    
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    $urlRouterProvider.otherwise('/home_page');
    // $urlRouterProvider.otherwise('/new_quiz');

    $stateProvider
        .state('home_page', {
            url: '/home_page',
            templateUrl: 'home_page'
        })
        .state('help', {
            url: '/help_page',
            templateUrl: 'help_page'
        })
        .state('about', {
            url: '/about_page',
            templateUrl: 'about_page'
        })
        .state('quiz_home', {
            url: '/quiz_home',
            templateUrl: 'quiz_home'
        })
        .state('student_home', {
            url: '/student_home',
            templateUrl: 'student_home'
        })
        .state('new_quiz', {
            url: '/new_quiz',
            templateUrl: 'new_quiz'
        })
        .state('post_home', {
            url: '/post_home',
            templateUrl: 'post_home'
        })
        .state('review_as', {
            url: '/review_as',
            templateUrl: 'review_as'
        })
        .state('review_application', {
            url: '/review_application',
            templateUrl: 'review_application'
        })
        .state('view_badge', {
            url: '/view_badge',
            templateUrl: 'view_badge'
        })
        .state('batch_perf', {
            url: '/batch_perf/:batch_id/:batch_name',
            templateUrl: 'batch_perf'
        })
        .state('batch_home', {
            url: '/batch_home',
            templateUrl: 'batch_home'
        });

});

r2_app.run(function($rootScope, $http, R2Serv) {

    $rootScope.ckEditorOptions = {
        toolbar: 'full',
        toolbar_full: [ //jshint ignore:line
            {
                name: 'basicstyles',
                items: ['Bold', 'Italic', 'Strike', 'Underline']
            },
            {name: 'paragraph', items: ['BulletedList', 'NumberedList', 'Blockquote']},
            {name: 'editing', items: ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {name: 'links', items: ['Link', 'Unlink', 'Anchor']},
            {name: 'tools', items: ['SpellChecker', 'Maximize']},
            '/',
            {
                name: 'styles',
                items: ['Format', 'FontSize', 'TextColor', 'PasteText', 'PasteFromWord', 'RemoveFormat']
            },
            {name: 'insert', items: ['Table', 'SpecialChar']},
            {name: 'forms', items: ['Outdent', 'Indent']},
            {name: 'clipboard', items: ['Undo', 'Redo']},
            {name: 'document', items: ['PageBreak', 'Source']}
        ],
        disableNativeSpellChecker: false,
        uiColor: '#FAFAFA',
        height: '200px',
        width: '100%'
    };

    $rootScope.student_count = '';
    $rootScope.quiz_count = '';
    $rootScope.batch_count = '';

    $rootScope.post_config = {
        headers: {
            "content-type": "application/x-www-form-urlencoded"
        }
    };

    $rootScope.get_all_counts = function() {
        
        var get_all_counts_req_data = {
            data: {
                username: "admin",
                password: "admin123"
            }
        };

        $http.post('/get_admin_counts/', JSON.stringify(get_all_counts_req_data), JSON.stringify($rootScope.post_config))
        .then(function(response) {
            R2Serv.console('\n\ndata received from the server for get_admin_counts: ', response);
            $rootScope.student_count = response.data.get_admin_counts.student_count;
            $rootScope.batch_count = response.data.get_admin_counts.batch_count;
            $rootScope.quiz_count = response.data.get_admin_counts.quiz_count;
            $rootScope.post_count = response.data.get_admin_counts.post_count;
            $rootScope.ass_count = response.data.get_admin_counts.ass_count;
            $rootScope.app_count = response.data.get_admin_counts.app_count;
            $rootScope.app_topic_count = response.data.get_admin_counts.app_topic_count;
            $rootScope.badge_count = response.data.get_admin_counts.badge_count;
        });
    }

    $rootScope.get_all_counts();

    $rootScope.is_blank = function(anything) {
        if(typeof anything === 'undefined') {
            return true;
        }
        else if(anything.trim() == '') {
            return true;
        }
        else {
            return false;
        }
    }

});

r2_app.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
                scope.$apply(function(){
                modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);

r2_app.service('R2Serv', function() {
    this.console = function(title, data) {
        console.log('R2Serv: ' + title + ': ', data);
    }

    this.handle_fail = function(res) {
        if (res.status == 'fail') {
            console.log('R2Serv.handle_fail: ' + res.message);
            swal('Something went wrong, please contact administrator!', '', 'warning');
            return true;
        }
        else {
            return false;
        }
    }
});