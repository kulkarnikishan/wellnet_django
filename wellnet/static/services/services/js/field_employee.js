/**
 * Created by prakash on 8/11/17.
 */
(function ($) {
    function init_select2_again() {
        var initial_number_of_branches = $('#reports_set-group > div.items').children("div[id^=reports_set-]").length - 1;
        console.log("init : " + initial_number_of_branches);
        setTimeout(function () {
            $("select#id_reports_set-" + initial_number_of_branches + "-state").next().remove();
            $("select#id_reports_set-" + initial_number_of_branches + "-state").djangoSelect2();
            $("select#id_reports_set-" + initial_number_of_branches + "-city").next().remove();
            $("select#id_reports_set-" + initial_number_of_branches + "-city").djangoSelect2();
            var legend_hash = initial_number_of_branches + 1;
            $("div#reports_set-" + initial_number_of_branches + " > legend").contents().filter(function () {
                return this.nodeType == 3 && $(this).is(":contains('#2')");
            }).replaceWith("#" + legend_hash + " ");
        }, 100);
    }

    $(document).ready(function () {
        setTimeout(function () {
            $("div.add-row > a > span.btn").on("click", init_select2_again);
        }, 1000);
    });


}(this.jQuery));