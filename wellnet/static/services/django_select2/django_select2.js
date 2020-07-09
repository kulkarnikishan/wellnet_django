(function ($) {

    var init = function ($element, options) {
        $element.select2(options);
    };

    var initHeavy = function ($element, options) {
        var settings = $.extend({
            ajax: {
                data: function (params) {
					var filter_model_id = $element.data('filter_model_id')
					if(filter_model_id != undefined && ($("#"+filter_model_id).val() == undefined && filter_model_id.match("^id_self") == null)) {
						alert("Select " + $element.data('filter_model_id').replace('id_', '').toUpperCase() + " option first");
					}
					if (filter_model_id != undefined && filter_model_id.match("^id_self") != null) {
						filter_val = ""+$element.data('filter_val');
					} else {
						filter_val = $("#"+$element.data('filter_model_id')).val();
					}
                    return {
                        term: params.term,
                        page: params.page,
						filter_model: $element.data('filter_model_id') ? $element.data('filter_model_id').replace('id_', '') : undefined,
						filter_val: filter_val,
                        field_id: $element.data('field_id')
                    };
                },
                processResults: function (data, page) {
                    return {
                        results: data.results,
                        pagination: {
                            more: data.more
                        }
                    };
                }
            }
        }, options);

        $element.select2(settings);
    };

    $.fn.djangoSelect2 = function (options) {
        var settings = $.extend({}, options);
        $.each(this, function (i, element) {
            var $element = $(element);
            if ($element.hasClass('django-select2-heavy')) {
                initHeavy($element, settings);
            } else {
                init($element, settings);
            }
        });
        return this;
    };

    $(function () {
        $('.django-select2').djangoSelect2();
    });

}(this.jQuery));
