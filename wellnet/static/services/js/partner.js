(function ($) {
    function sameAsOwner(check) {
        if ($(check).is(':checked')) {
            var name = $("#id_partnerasowner_set-0-name").val();
            var gender = $("#id_partnerasowner_set-0-gender").val();
            var gender_text = $("#select2-id_partnerasowner_set-0-gender-container").html()
            var landline = $("#id_partnerasowner_set-0-landline").val();
            var mobile = $("#id_partnerasowner_set-0-mobile_number").val();
            var address = $("#id_partnerasowner_set-0-address").val();
            var email = $("#id_partnerasowner_set-0-email").val();
            if (name == '' || gender == '' || landline == '' || mobile == '' || address == '' || email == '') {
                alert("Please fill Owner details before copying to Authorized Person details.");
                $(check).attr("checked", false);
            } else {
                var id_prefix = $(check).attr("id").replace("same_as_owner", "");
                $("#" + id_prefix + "authorized_person_name").val(name);
                $("#" + id_prefix + "authorized_person_gender").val(gender);
                $("#select2-" + id_prefix + "authorized_person_gender-container").html(gender_text);
                $("#" + id_prefix + "authorized_person_landline").val(landline);
                $("#" + id_prefix + "authorized_person_mobile_number").val(mobile);
                $("#" + id_prefix + "authorized_person_address").val(address);
                $("#" + id_prefix + "authorized_person_email").val(email);
            }
        }
    }

    function linkNewCheckBox() {
        $("input[id$=same_as_owner]").each(function (index, element) {
            $(this).click(function () {
                sameAsOwner(element);
            });
        });
    }

    function init_select2_again() {
        var initial_number_of_branches = $('#partnerbranch_set-group > div.items').children("div[id^=partnerbranch_set-]").length - 1;
        console.log("init : " + initial_number_of_branches);
        setTimeout(function () {
            $("select#id_partnerbranch_set-" + initial_number_of_branches + "-state").next().remove();
            $("select#id_partnerbranch_set-" + initial_number_of_branches + "-state").djangoSelect2();
            $("select#id_partnerbranch_set-" + initial_number_of_branches + "-city").next().remove();
            $("select#id_partnerbranch_set-" + initial_number_of_branches + "-city").djangoSelect2();
            $("select#id_partnerbranch_set-" + initial_number_of_branches + "-authorized_person_gender").next().remove();
            $("select#id_partnerbranch_set-" + initial_number_of_branches + "-authorized_person_gender").djangoSelect2();
            var legend_hash = initial_number_of_branches + 1;
            $("div#partnerbranch_set-" + initial_number_of_branches + " > legend").contents().filter(function () {
                return this.nodeType == 3 && $(this).is(":contains('#2')");
            }).replaceWith("#" + legend_hash + " ");
        }, 100);
    }

    function check_value_for_select() {
        var selected = $("select#id_manager option:selected").html();
        if (selected != undefined && selected != '') {
            if ($("#select2-id_manager-container").html() == "") {
                $("#select2-id_manager-container").html(selected);
            }
        }
    }

    function enable_edit_function() {
        var edit = $("#change_id_manager");
        var customer_pk = $("select#id_manager").val();
        if (edit.length != 0 && customer_pk != undefined && customer_pk != "") {
            var href_val = edit.attr("data-href-template").replace("__fk__", customer_pk);
            edit.attr("href", href_val);
        }
    }
    function showHideAddBranch(val) {
        console.log(val)
        if (val=='1'){
            $(".add-row").hide()
        }
        else{
            $(".add-row").show()
        }
    }

    $(document).ready(function () {
        $('#partnerbranch_set-group').bind("DOMSubtreeModified", linkNewCheckBox);
        setTimeout(function () {
            $("div.add-row > a > span.btn").on("click", init_select2_again);
        }, 1000);
         $('#id_GSTIN').keyup(function() {
        this.value = this.value.toLocaleUpperCase();
    });
	$('#id_dealer_code').keyup(function() {
        this.value = this.value.toLocaleUpperCase();
    });
        linkNewCheckBox();
        $('select#id_manager').bind("DOMSubtreeModified", check_value_for_select);
        $("select#id_manager").on('change', enable_edit_function);
        $("select#id_manager").on('change', enable_edit_function);
        if ($("#id_dealership_category").val() != undefined && $("#id_dealership_category").val() != '') {
            showHideAddBranch($("#id_dealership_category").val());
        }
          $("#id_dealership_category").on('change', function () {
            if ($(this).val() != undefined && $(this).val() != '') {
                showHideAddBranch($(this).val());
            }
        });

    });

}(this.jQuery));
