
fields = [
    { 'first_name': "{% url 'frontend:candidate-first-name-update' %}" },
    { 'middle_name': "{% url 'frontend:candidate-middle-name-update' %}" },
    { 'last_name': "{% url 'frontend:candidate-last-name-update' %}" },
    { 'mobile_number': "{% url 'frontend:candidate-mobile-number-update'%}" },
    { 'address': "{% url 'frontend:candidate-address-update' %}" },
    { 'fathers_name': "{% url 'frontend:candidate-fathers-name-update' %}" },
    { 'mothers_name': "{% url 'frontend:candidate-mothers-name-update' %}" },
]


dropDownFields = [
    {
        'gender': ["{% url 'frontend:candidate-gender-update' %}", "{% url 'api:gender-list' %}"]
    },
    {
        'nationality': ["{% url 'frontend:candidate-nationality-update' %}", "{% url 'api:nationality' %}"]
    },
    {
        'religion': ["{% url 'frontend:candidate-religion-update' %}", "{% url 'api:religion' %}"]
    },
    {
        'marital_status': ["{% url 'frontend:candidate-marital-status-update' %}", "{% url 'api:marital-status' %}"]
    }
]

function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
}

dropDownFields.forEach((field, index) => {
    var key = Object.keys(field);
    var value = field[key];
    editableDropdown(key, value[0], value[1])
})

fields.forEach((field, index) => {
    var key = Object.keys(field)
    var value = field[key];

    editable(key, value)
});

function editable(className, url) {
    var thisClass = $(`.${className}`);
    $(thisClass).editable(url, {
        type: "text",
        placeholder: '----',
        blur: 'ignore',
        callback: function (result, settings, submitdata) {
            $('.inline-error').remove();
            var response = JSON.parse(result);
            var status = response.status;
            if (status) {
                if (response.data) {
                    thisClass.text(response.data)
                } else {
                    thisClass.text("----")
                }
            } else {
                for (let error in response.errors) {
                    thisClass.text(submitdata.previousdata)
                    thisClass.parent().append(`<span style="color:red;" class="inline-error">${response.errors[error]}</span>`)
                    thisClass.click();
                }

                setTimeout(function () {
                    $('.inline-error').fadeOut('fast');
                }, 1000);
            }

        },
        submitcssclass: 'btn btn-success inline-edit-button',
        select: true,
        submit: 'Save',
        cancel: 'Cancel',
        cancelcssclass: 'btn btn-danger',
        submitdata: function (revert, settings) {
            var submitdata = {};
            submitdata['csrfmiddlewaretoken'] = `{{ csrf_token }}`;
            submitdata[className] = thisClass.find('input').val()
            submitdata['previousdata'] = revert
            return submitdata;
        }
    }).on('click', function () {
        $(this).find('input').addClass("form-control").css({ 'width': '100%' });
    });
}




function editableDropdown(className, url, url2) {
    var thisClass = $(`.${className}`);

    $.getJSON(url2, function (data) {
        $(thisClass).editable(url, {
            type: 'select',
            data: data,
            submitdata: function () {
                var submitdata = {};
                submitdata['csrfmiddlewaretoken'] = `{{ csrf_token }}`;
                submitdata[className] = thisClass.find('select :selected').val()
                return submitdata;
            },
            callback: function (result, settings, submitdata) {
                var response = JSON.parse(result);
                var status = response.status;
                if (status) {
                    thisClass.text(settings.data[response.data])
                } else {
                    for (let error in response.errors) {
                        thisClass.text(submitdata.previousdata)
                        thisClass.parent().append(`<span style="color:red;" class="inline-error">${response.errors[error]}</span>`)
                        thisClass.click();
                    }

                    setTimeout(function () {
                        $('.inline-error').fadeOut('fast');
                    }, 1000);
                }
            },
            submit: 'Save',
            cssClass: 'form-control',
            submitcssclass: 'btn btn-success inline-edit-button',
            cancel:'Cancel',
            cancelcssclass:'btn btn-danger',
        }).on('click', function () {
            $(this).find('select').addClass("form-control").css({ 'width': '100%' });
        });
    })

}

editableDatePikcer('dob', "{% url 'frontend:candidate-dob-update' %}")

function editableDatePikcer(className, url) {
    var thisClass = $(`.${className}`);
    var date = $(thisClass).text();

    $(thisClass).editable(url, {
        type: "datepicker",
        submit: "OK",
        datepicker: {
            format: "yy-mm-dd",
            defaultDate: formatDate(date)
        },
        cancel:'Cancel',
        cancelcssclass:'btn btn-danger',
        blur:'ignore',
        submitdata: function (revert, settings) {
            var submitdata = {};
            submitdata['csrfmiddlewaretoken'] = `{{ csrf_token }}`;
            submitdata[className] = $('.dob').find('input').val()
            submitdata['previousdata'] = revert
            return submitdata;
        },
        callback: function (result, settings, submitdata) {
            $('.inline-error').remove();
            var response = JSON.parse(result);
            var status = response.status;
            if (status) {
                if (response.data) {
                    thisClass.text(moment(response.data).format('ll'))
                } else {
                    thisClass.text("----")
                }
            } else {
                for (let error in response.errors) {
                    thisClass.text(submitdata.previousdata)
                    thisClass.parent().append(`<span style="color:red;" class="inline-error">${response.errors[error]}</span>`)
                    thisClass.click();
                }

                setTimeout(function () {
                    $('.inline-error').fadeOut('fast');
                }, 1000);
            }

        },
        submitcssclass: 'btn btn-success inline-edit-button',
        select: true,
        submit: 'Save',
    }).on('click', function () {
        $(this).find('input').addClass("form-control").css({ 'width': '100%' });
    });;
}
