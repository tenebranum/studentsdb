function initJournal(){
	var indicator = $('#ajax-progress-indicator');

	$('.day-box input[type="checkbox"]').click(function(event){
		var box = $(this);
		$.ajax(box.data('url'), {
			'type':'POST',
			'async':true,
			'dataType':'json',
			'data':{
				'pk':box.data('student-id'),
				'date':box.data('date'),
				'present':box.is(':checked')?'1':'',
				'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
			},
			'beforeSend':function(xhr,settings){
				indicator.show();
			},
			'error':function(xhr,status,error){
				alert(error);
				indicator.hide();
			},
			'success':function(data,status,xhr){
				indicator.hide();
			}
		});
	});
}

function initGroupSelector(){
	$('#group-selector select').change(function(event){
		var group = $(this).val();
		if(group){
			$.cookie('current_group',group,{'path':'/','expires':365});
		}
		else{
			$.removeCookie('current_group',{'path':'/'});
		}

		location.reload(true);

		return true;
	})
}

function initDateField(){
	$('input.dateinput').datetimepicker({
		'format':'YYYY-MM-DD'
	}).on('dp.hide',function(event){
		$(this).blur();
	});
}

function initEditStudentForm(form,modal){
	initDateField();
	form.find('input[name="cancel_button"]').click(function(event){
		modal.modal('hide');
		return false;
	});

	form.ajaxForm({
		'dataType':'html',
		'error':function(){
			alert(gettext('Server error, try later...'));
			return false;
		},
		'success':function(data,status,xhr){
			var html = $(data), newform = html.find('#content-column form');
			modal.find('.modal-body').html(html.find('.alert'));
			if(newform.length>0){
				modal.find('.modal-body').append(newform);
				initEditStudentForm(newform,modal);
			}
			else{
				setTimeout(function(){location.reload(true);},500);
			}
		}
	});
}

function initEditStudentPage(){
	$('a.student-edit-link').click(function(event){
		var link = $(this);
		$.ajax({
			'url':link.attr('href'),
			'dataType':'html',
			'type':'get',
			'success':function(data,status,xhr){

				if (status != 'success'){
					alert(gettext('Server error, try later...'));
					return false;
				}
				var modal = $('#myModal');
				html = $(data),form = html.find('#content-column form');
				modal.find('.modal-title').html(html.find('#content-column h2').text());
				modal.find('.modal-body').html(form);

				initEditStudentForm(form,modal);

				modal.modal({
					'show':true,
					'keyboard':false,
					'backdrop':false
				});
			},
			'error':function(){
				alert(gettext('Server error, try later...'));
				return false;
			}
		});
		return false;
	});
}

$(document).ready(function(){
	initJournal();
	initGroupSelector();
	initDateField();
	initEditStudentPage();
});