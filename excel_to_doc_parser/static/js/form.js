$(function () {
    $('#smartwizard').smartWizard({
        selected: 0,
        theme: 'round',
        justified: true,
        autoAdjustHeight: true,
        backButtonSupport: true,
        enableUrlHash: true,
        transition: {
            animation: 'fade',
            speed: '400',
        },
        toolbar: {
            position: 'bottom',
            showNextButton: true,
            showPreviousButton: true,
            extraHtml: '<button class="btn btn-success" name="end" value="generate" onclick="generate_output()" type="submit">Закончить</button>' // Extra html to show on toolbar
        },
        anchor: {
            enableNavigation: true,
            enableNavigationAlways: true, // Activates all anchors clickable always
            enableDoneState: true,
            markPreviousStepsAsDone: true,
            unDoneOnBackNavigation: false,
            enableDoneStateNavigation: true
        },
        keyboard: {
            keyNavigation: true,
            keyLeft: [37],
            keyRight: [39]
        },
        lang: {
            next: 'Далее',
            previous: 'Назад'
        },
        disabledSteps: [], // Array Steps disabled
        errorSteps: [], // Array Steps error
        warningSteps: [], // Array Steps warning
        hiddenSteps: [], // Hidden steps
        getContent: null // Callback function for content loading
    });
    $('.drag').draggable({
        appendTo: 'body',
        helper: 'clone'
    });

    $('#dropzone').droppable({
        activeClass: 'active',
        hoverClass: 'hover',
        accept: ":not(.ui-sortable-helper)", // Reject clones generated by sortable
        drop: function (e, ui) {
            var $el = $(ui.draggable);
            // $el.click(function () {
            //     $('#dropzone').append(ui.draggable);
            //     ui.draggable.remove();
            // });
            $(this).append($el);
            $('#smartwizard').smartWizard("fixHeight");
        }
    }).sortable({
        items: '.drop-item',
        sort: function () {
            // gets added unintentionally by droppable interacting with sortable
            // using connectWithSortable fixes this, but doesn't allow you to customize active/hoverClass options
            // $(this).removeClass("active");
        }
    });
    $('#modules').droppable({
        activeClass: 'active',
        hoverClass: 'hover',
        accept: ":not(.ui-sortable-helper)", // Reject clones generated by sortable
        drop: function (e, ui) {
            var $el = $(ui.draggable);
            // $el.click(function () {
            //     $('#dropzone').append(ui.draggable);
            //     ui.draggable.remove();
            // });
            $(this).append($el);
            $('#smartwizard').smartWizard("fixHeight");
        }
    }).sortable({
        items: '.drop-item',
        sort: function () {
            // gets added unintentionally by droppable interacting with sortable
            // using connectWithSortable fixes this, but doesn't allow you to customize active/hoverClass options
            // $(this).removeClass("active");
        }
    });
});
let added_sections = [];
$("#smartwizard").on("showStep", function (e, anchorObject, stepIndex, stepDirection, stepPosition) {
    if (stepIndex === 3) {
        let section = document.getElementsByClassName("sections");
        let output_div = document.getElementById("section");
        let dict = {};
        for (let i = 0; i < section.length; i++) {
            dict[section[i].children[0].value] = section[i].children[1].value;
        }
        let sections = document.getElementById("theme");
        for (let [key, value] of Object.entries(dict)) {
            if (key && added_sections.indexOf(key) === -1) {
                added_sections.push(key);
                //Create option in select
                let section_content = document.createElement("option");
                section_content.textContent = key;
                section_content.setAttribute("value", iuliia.translate(key, iuliia.WIKIPEDIA));
                sections.appendChild(section_content);
                //Create div for all themes
                let theme = document.createElement("div");
                theme.setAttribute("id", iuliia.translate(key, iuliia.WIKIPEDIA))
                theme.setAttribute("class", "d-none");
                //Create hours input field
                // let hour = document.createElement("div");
                // hour.setAttribute("class", "row mb-3 " + iuliia.translate(key, iuliia.WIKIPEDIA));
                // let hour_label = document.createElement("label");
                // hour_label.textContent = "Часы";
                // hour_label.setAttribute("for", "hour");
                // hour_label.setAttribute("class", "col-sm-2 col-form-label");
                // hour.appendChild(hour_label);
                // let hour_input_div = document.createElement("div");
                // hour_input_div.setAttribute("class", "col-sm-10");
                // let hour_input = document.createElement("input");
                // hour_input.setAttribute("value", value.toString());
                // hour_input.setAttribute("class", "form-control");
                // hour_input.setAttribute("type", "number");
                // hour_input.setAttribute("readonly", "");
                // hour_input.setAttribute("id", "hour");
                // hour_input_div.appendChild(hour_input);
                // hour.appendChild(hour_input_div);
                // theme.appendChild(hour);
                //Create content input field
                let content = document.createElement("div");
                content.setAttribute("class", "mb-3 " + iuliia.translate(key, iuliia.WIKIPEDIA));
                let content_label = document.createElement("label");
                content_label.textContent = "Содержание";
                content_label.setAttribute("for", "content");
                content_label.setAttribute("class", "form-label");
                content.appendChild(content_label);
                let content_textarea = document.createElement("textarea");
                content_textarea.setAttribute("placeholder", "Содержание раздела");
                content_textarea.setAttribute("class", "form-control");
                content_textarea.setAttribute("name", "content");
                content_textarea.setAttribute("id", "content");
                content.appendChild(content_textarea);
                theme.appendChild(content);
                output_div.appendChild(theme);
            }
        }
        document.getElementById("theme").addEventListener("input", function () {
            let vis = document.getElementsByClassName('vis')
            let target = document.getElementById(this.value);
            // console.log("vis", vis, "target", target);
            if (vis !== null) {
                for (const visElement of vis) {
                    visElement.className = visElement.className.replace("vis", "d-none");
                    // console.log(visElement.className);
                }
            }
            if (target !== null && target.value !== "choose_theme") {
                target.className = target.className.replace("d-none", "vis");
            }
            if (target.value === "choose_theme") {
                for (const visElement of vis) {
                    visElement.className = visElement.className.replace("vis", "d-none");
                    // console.log(visElement.className);
                }
            }
            $('#smartwizard').smartWizard("fixHeight");
        });
    }
});

function addInputs() {
    document.getElementById("addInputGroup").remove();
    document.getElementById("result_block").remove();
    let new_div = document.createElement("div");
    document.getElementById("sections").appendChild(new_div);
    new_div.setAttribute("class", "mb-3");
    let new_div_group = document.createElement("div");
    new_div.appendChild(new_div_group);
    new_div_group.setAttribute("class", "input-group sections");
    let section_input = document.createElement("input");
    new_div_group.appendChild(section_input);
    section_input.setAttribute("class", "form-control section");
    section_input.setAttribute("type", "text");
    section_input.setAttribute("name", "section");
    let hours_input_lections = document.createElement("input");
    new_div_group.appendChild(hours_input_lections);
    hours_input_lections.setAttribute("class", "form-control hours_lections");
    hours_input_lections.setAttribute("type", "number");
    hours_input_lections.setAttribute("name", "hours_lections");
    let hours_input_labs = document.createElement("input");
    new_div_group.appendChild(hours_input_labs);
    hours_input_labs.setAttribute("class", "form-control hours_labs");
    hours_input_labs.setAttribute("type", "number");
    hours_input_labs.setAttribute("name", "hours_labs");
    let hours_input_seminars = document.createElement("input");
    new_div_group.appendChild(hours_input_seminars);
    hours_input_seminars.setAttribute("class", "form-control hours_seminars");
    hours_input_seminars.setAttribute("type", "number");
    hours_input_seminars.setAttribute("name", "hours_seminars");
    let hours_input_srs = document.createElement("input");
    new_div_group.appendChild(hours_input_srs);
    hours_input_srs.setAttribute("class", "form-control hours_srs");
    hours_input_srs.setAttribute("type", "number");
    hours_input_srs.setAttribute("name", "hours_srs");
    let new_result_block = document.createElement("div");
    new_result_block.setAttribute("class", "mb-3");
    new_result_block.setAttribute("id", "result_block");
    let new_result_section = document.createElement("div");
    new_result_section.setAttribute("class", "input-group");
    let result_text = document.createElement("input");
    result_text.value = "Итого";
    result_text.setAttribute("type", "text");
    result_text.setAttribute("class", "form-control");
    result_text.setAttribute("readonly", "");
    new_result_section.appendChild(result_text);
    let hours_lections_result = document.createElement("input");
    let hours = 0;
    let sections = document.getElementsByClassName("hours_lections");
    for (let section of sections) {
        if (section.value !== '') {
            hours += parseInt(section.value);
        }
    }
    hours_lections_result.value = hours;
    hours_lections_result.setAttribute("id", "hours_lections_result");
    hours_lections_result.setAttribute("type", "number");
    hours_lections_result.setAttribute("class", "form-control");
    hours_lections_result.setAttribute("readonly", "");
    new_result_section.appendChild(hours_lections_result);
    let hours_labs_result = document.createElement("input");
    hours = 0;
    sections = document.getElementsByClassName("hours_labs");
    for (let section of sections) {
        if (section.value !== '') {
            hours += parseInt(section.value);
        }
    }
    hours_labs_result.value = hours;
    hours_labs_result.setAttribute("id", "hours_labs_result");
    hours_labs_result.setAttribute("type", "number");
    hours_labs_result.setAttribute("class", "form-control");
    hours_labs_result.setAttribute("readonly", "");
    new_result_section.appendChild(hours_labs_result);
    let hours_seminars_result = document.createElement("input");
    hours = 0;
    sections = document.getElementsByClassName("hours_seminars");
    for (let section of sections) {
        if (section.value !== '') {
            hours += parseInt(section.value);
        }
    }
    hours_seminars_result.value = hours;
    hours_seminars_result.setAttribute("id", "hours_seminars_result");
    hours_seminars_result.setAttribute("type", "number");
    hours_seminars_result.setAttribute("class", "form-control");
    hours_seminars_result.setAttribute("readonly", "");
    new_result_section.appendChild(hours_seminars_result);
    let hours_srs_result = document.createElement("input");
    hours = 0;
    sections = document.getElementsByClassName("hours_srs");
    for (let section of sections) {
        if (section.value !== '') {
            hours += parseInt(section.value);
        }
    }
    hours_srs_result.value = hours;
    hours_srs_result.setAttribute("id", "hours_srs_result");
    hours_srs_result.setAttribute("type", "number");
    hours_srs_result.setAttribute("class", "form-control");
    hours_srs_result.setAttribute("readonly", "");
    new_result_section.appendChild(hours_srs_result);
    new_result_block.appendChild(new_result_section);
    document.getElementById("sections").appendChild(new_result_block);
    let new_button = document.createElement("button");
    document.getElementById("sections").appendChild(new_button);
    new_button.setAttribute("class", "btn btn-primary");
    new_button.setAttribute("type", "button");
    new_button.setAttribute("id", "addInputGroup");
    new_button.setAttribute("onclick", "addInputs()");
    new_button.textContent = "Добавить раздел";
    $('#smartwizard').smartWizard("fixHeight");
}

function addInputsMarks() {
    document.getElementById("addInputGroupMarks").remove();
    let new_div = document.createElement("div");
    document.getElementById("marks").appendChild(new_div);
    new_div.setAttribute("class", "mb-3");
    let new_div_group = document.createElement("div");
    new_div.appendChild(new_div_group);
    new_div_group.setAttribute("class", "input-group marks");
    let section_input = document.createElement("input");
    new_div_group.appendChild(section_input);
    section_input.setAttribute("class", "form-control mark");
    section_input.setAttribute("type", "text");
    section_input.setAttribute("name", "mark");
    let hours_input = document.createElement("input");
    new_div_group.appendChild(hours_input);
    hours_input.setAttribute("class", "form-control description");
    hours_input.setAttribute("type", "text");
    hours_input.setAttribute("name", "description");
    let new_button = document.createElement("button");
    document.getElementById("marks").appendChild(new_button);
    new_button.setAttribute("class", "btn btn-primary");
    new_button.setAttribute("type", "button");
    new_button.setAttribute("id", "addInputGroupMarks");
    new_button.setAttribute("onclick", "addInputsMarks()");
    new_button.textContent = "Добавить оценку";
    $('#smartwizard').smartWizard("fixHeight");
}

function generate_output() {
    //generate input with all sections
    let sections = document.getElementsByClassName("section");
    let hours_lections = document.getElementsByClassName("hours_lections");
    let hours_labs = document.getElementsByClassName("hours_labs");
    let hours_seminars = document.getElementsByClassName("hours_seminars");
    let hours_srs = document.getElementsByClassName("hours_srs");
    let contents = document.getElementById("section");
    let sections_str = "";
    if (sections.length === hours_lections.length && sections.length === contents.children.length) {
        for (let i = 0; i < sections.length; i++) {
            sections_str += sections[i].value + ":" + hours_lections[i].value + ":" + hours_labs[i].value + ":" + hours_seminars[i].value + ":" + hours_srs[i].value + ":" + contents.children[i].children[0].children[1].value + ";";
        }
        let all_sections = document.createElement("input");
        all_sections.value = sections_str;
        all_sections.setAttribute("type", "hidden");
        all_sections.setAttribute("name", "all_sections");
        document.getElementById("sections").appendChild(all_sections);
    } else {
        let error_input = document.createElement("input");
        error_input.value = "error:sections-hour-mismatch";
        error_input.setAttribute("type", "hidden");
        error_input.setAttribute("name", "all_sections");
        document.getElementById("sections").appendChild(error_input);
    }
    //generate input with all modules
    let modules = document.getElementById("dropzone");
    let modules_str = "";
    for (let module of modules.children) {
        modules_str += module.textContent + ";";
    }
    let all_module = document.createElement("input");
    all_module.value = modules_str;
    all_module.setAttribute("type", "hidden");
    all_module.setAttribute("name", "all_modules");
    document.getElementById("dropzone").appendChild(all_module);
    //generate input with all marks
    let marks = document.getElementsByClassName("marks");
    let description = document.getElementsByClassName("description");
    let marks_str = "";
    for (let i = 0; i < marks.length; i++) {
        marks_str += marks[i].children[0].value + ":" + description[i].value + ";";
    }
    let all_marks = document.createElement("input");
    all_marks.value = marks_str;
    all_marks.setAttribute("type", "hidden");
    all_marks.setAttribute("name", "all_marks");
    document.getElementById("marks").appendChild(all_marks);
}

window.onload = function () {
    let max_hours = document.getElementById("max_hours");
    let textareas = document.getElementsByTagName("textarea");
    for (const textarea of textareas) {
        textarea.addEventListener('mouseout', function () {
            $('#smartwizard').smartWizard("fixHeight");
        });
    }
    document.getElementById("score_system").addEventListener('change', function () {
        if (this.checked) {
            document.getElementById("brs").className = "mb-3";
        } else {
            document.getElementById("brs").className = "mb-3 d-none";
        }
        $('#smartwizard').smartWizard("fixHeight");
    })
    document.getElementById("sections").addEventListener('change', function () {
        let hours = 0;
        let hours_list = document.getElementsByClassName("hour");
        for (let hoursListElement of hours_list) {
            hours += parseInt(hoursListElement.value);
        }
        if (hours > max_hours) {
            alert("Число часов превышено");
        }
        document.getElementById("hours_result").value = hours;
    })
};