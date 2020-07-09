/**
 * Created by prakash on 3/11/17.
 */
(function ($) {
    function showHideDateFields(val) {
        switch (val) {
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':

                $("#id_to_date").show();
                $(".field-to_date").show();
                $(".field-from_date").show();
                $("#id_from_date").show();
                break;
            case '6':
            case '7':
                 $("#id_to_date").hide();
                $("#id_from_date").hide();
                 $(".field-to_date").hide();
                $(".field-from_date").hide();
                break;
        }
    }


    $(document).ready(function () {
        $("#id_model_type").on('change', function () {
            if ($(this).val() != undefined && $(this).val() != '') {
                showHideDateFields($(this).val());
            }
        })
        showHideDateFields($("#id_model_type").val());
        $('[name="_save"]').val("Save Report");
        $('[name="_addanother"]').hide()
        $('[name="_continue"]').hide()

    });
}(this.jQuery));