var QUOTES = [];

var overall_idx = 0;
var idx = 0;
var hint_needed = true;
var showing_quote = false;
var waiting_on_quotes = false;
var show_endcap_next = false;

function show_endcap() {
  $('#new_quote').fadeIn();
}

function show_hint() {
	if (hint_needed) {
		$('#hint').fadeIn();
	}
}

function replace_quotes(data) {
  QUOTES = data.quotes;
  waiting_on_quotes = false;
  if (QUOTES.length == 0) {
    show_endcap_next = true;
  }
}

function get_new_quotes() {
  overall_idx += QUOTES.length;
  idx = 0;
  
  waiting_on_quotes = true;
  $.ajax('/get_quotes', {
    'dataType': 'json',
    'data': {
      'start': overall_idx,
      'count': 5
    },
    success: replace_quotes
  });
}

function on_hitarea_clicked(evt) {
  if (waiting_on_quotes || showing_quote) {
    return;
  }
	hint_needed = false;
	$('#hint').remove();

  var quote = QUOTES[idx];
  var div = $('<div class="quote"></div>')
  div.text(quote.data);
  idx++;
  if (idx >= QUOTES.length) {
    get_new_quotes();
  }
  div.css('left', evt.clientX).css('top', evt.clientY);
  $('#frame').append(div)

	showing_quote = true;
  setTimeout(function() {
    div.fadeOut(400, function() {
			showing_quote = false;
      div.remove();
			if (show_endcap_next) {
				show_endcap();
			}
    });
  }, quote.data.length * 34);
}

function on_quote_submission() {
	if ($('#quote').val().length == 0) {
		$('#error').text('You should try entering a quote first...');
		return;
	}

	if ($('#quote').val().match(/^\s*$/)) {
		$('#error').text('Try entering a quote with some actual letters...');
		return;
	}

	$('#error').text('');
  $.ajax('/add_quote', {
    'method': 'POST',
    'data': {
      'last_idx': overall_idx,
      'quote': $('#quote').val(),
			'token': TOKEN
    },
    'success': function(data) {
			if (data['error']) {
				$('#error').text(data['error']);
				if (data['last_idx']) {
					overall_idx = data['last_idx'];
				}
			} else {
				window.location.reload();
			}
    },
		'error': function() {
			$('#error').text('An unexpected error has occurred. Try again?');
		}
  });
}

get_new_quotes();

$(function() {
  $('#hitarea').click(on_hitarea_clicked);
  $('#quote-submit').click(on_quote_submission);
	setTimeout(show_hint, 3500);
});
