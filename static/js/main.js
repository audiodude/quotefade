var QUOTES = [];

var overall_idx = 0;
var idx = 0;
var waiting_on_quotes = false;
var show_endcap_next = false;

function show_endcap() {
  $('#new_quote').fadeIn();
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
      'count': 2
    },
    success: replace_quotes
  });
}

function on_frame_clicked(evt) {
  if (waiting_on_quotes) {
    return;
  }
  var quote = QUOTES[idx];
  var div = $('<div></div>')
  div.text(quote.data);
  idx++;
  if (idx >= QUOTES.length) {
    get_new_quotes();
  }
  div.css('left', evt.clientX).css('top', evt.clientY);
  $('#frame').append(div)
  setTimeout(function() {
    div.fadeOut(400, function() {
      div.remove();
    });
    if (show_endcap_next) {
      show_endcap();
    }
  }, quote.data.length * 34);
}

function on_quote_submission() {
  $.ajax('/add_quote', {
    'method': 'POST',
    'data': {
      'last_idx': overall_idx,
      'quote': $('#quote').val()
    },
    'success': function() {
      window.location.reload();
    }
  });
}

get_new_quotes();

$(function() {
  $('#frame').click(on_frame_clicked);
  $('#quote-submit').click(on_quote_submission);
});
