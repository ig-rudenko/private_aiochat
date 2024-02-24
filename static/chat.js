let sock;
// ---- ws://127.0.0.1:8080/ws/room_name
try{
    sock = new WebSocket('ws://' + window.location.host + WS_URL);
}
catch (err) {
    sock = new WebSocket('wss://' + window.location.host + WS_URL);
}

const $chatArea = $('.current-chat-area')
const $messagesContainer = $('#messages')
const service_msg = '<div class="service-msg">{text}</div>'
const msg_template = `
<div class="media-body">
    <div class="media">
        <div class="media-body">
            <em>@{username}</em> <small class="text-muted">| {time}</small>
            <br>{text}
        </div>
    </div>
</div>`


function showMessage(message) {
    let msg;
    var data = jQuery.parseJSON(message.data);
    var date = new Date(data.created_at);
    if (data.cmd) {
        if (data.cmd === 'empty') {
            $messagesContainer.empty();
            return;
        }
    } else if (data.user) {
        msg = msg_template
            .replace('{username}', data.user)
            .replace('{text}', data.text)
            .replace('{time}', date.toLocaleString("ru"));

    } else {
        msg = service_msg.replace('{text}', data.text.split('\n').join('<br>'));
    }
    $messagesContainer.append('<li class="media">' + msg + '</li>');
    $chatArea.scrollTop($messagesContainer.height());
}

$(document).ready(() => {
    $chatArea.scrollTop($messagesContainer.height());

    $('#send').on('submit', event => {
        event.preventDefault();
        const $message = $(event.target).find('input[name="text"]');
        sock.send($message.val());
        $message.val('').focus();
    });

    sock.onopen = event => {
        console.log(event);
        console.log('Connection to server started');
    };

    sock.onclose = event => {
        console.log(event);
        if(event.wasClean){
            console.log('Clean connection end');
        } else {
            console.log('Connection broken');
        }
        window.location.assign('/');
    };

    sock.onerror = error => console.log(error);

    sock.onmessage = showMessage;
});
