/* chat.js — live chat widget: toggle, send, polling, localStorage */
(function () {
  var body = document.body;
  var csrf = body.dataset.csrf;
  var urlChatSend = body.dataset.urlChatSend;
  var urlChatMessages = body.dataset.urlChatMessages;

  var chatOpen = false;
  var chatPollingTimer = null;
  var chatLastId = 0;
  var chatUnreadCount = 0;

  setTimeout(function () {
    var bubble = document.getElementById('chatBubble');
    if (bubble && !chatOpen) {
      bubble.classList.add('show');
      setTimeout(function () { bubble.classList.remove('show'); }, 5000);
    }
  }, 5000);

  window.toggleChat = function () {
    chatOpen = !chatOpen;
    document.getElementById('chatPanel').classList.toggle('open', chatOpen);
    document.getElementById('chatTrigger').classList.toggle('active', chatOpen);
    var bubble = document.getElementById('chatBubble');
    if (bubble) bubble.classList.remove('show');
    var icon = document.getElementById('chatTriggerIcon');
    if (icon) icon.classList.remove('pulse');
    if (chatOpen) {
      chatUnreadCount = 0;
      updateUnreadBadge();
      var name = localStorage.getItem('chatName');
      if (name) {
        document.getElementById('chatNameForm').style.display = 'none';
        document.getElementById('chatInputArea').style.display = 'flex';
        document.getElementById('chatInput').focus();
      }
      startPolling();
      scrollChatDown();
    } else {
      stopPolling();
    }
  };

  window.saveChatName = function () {
    var input = document.getElementById('chatNameInput');
    var name = input.value.trim();
    if (!name) { input.focus(); return; }
    localStorage.setItem('chatName', name);
    document.getElementById('chatNameForm').style.display = 'none';
    document.getElementById('chatInputArea').style.display = 'flex';
    document.getElementById('chatInput').focus();
  };

  window.sendChatMessage = function () {
    var input = document.getElementById('chatInput');
    var text = input.value.trim();
    if (!text) return;
    input.value = '';

    var name = localStorage.getItem('chatName') || '';

    appendMsg('visitor', text);

    fetch(urlChatSend, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf
      },
      body: JSON.stringify({ text: text, name: name })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success && data.message) {
        chatLastId = Math.max(chatLastId, data.message.id);
      }
      if (!chatPollingTimer) startPolling();
    })
    .catch(function () {});
  };

  function appendMsg(sender, text) {
    var container = document.getElementById('chatMessages');
    var div = document.createElement('div');
    div.className = 'chat-msg chat-msg-' + sender;
    div.textContent = text;
    container.appendChild(div);
    scrollChatDown();
  }

  function scrollChatDown() {
    var el = document.getElementById('chatMessages');
    setTimeout(function () { el.scrollTop = el.scrollHeight; }, 50);
  }

  function pollMessages() {
    fetch(urlChatMessages + '?after=' + chatLastId)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.messages && data.messages.length) {
          data.messages.forEach(function (m) {
            if (m.id > chatLastId) {
              chatLastId = m.id;
              if (m.sender === 'admin') {
                appendMsg('admin', m.text);
                if (!chatOpen) {
                  chatUnreadCount++;
                  updateUnreadBadge();
                }
              }
            }
          });
        }
      })
      .catch(function () {});
  }

  function startPolling() {
    if (chatPollingTimer) return;
    pollMessages();
    chatPollingTimer = setInterval(pollMessages, 4000);
  }

  function stopPolling() {
    if (chatPollingTimer) {
      clearInterval(chatPollingTimer);
      chatPollingTimer = null;
    }
  }

  function updateUnreadBadge() {
    var badge = document.getElementById('chatUnread');
    if (chatUnreadCount > 0) {
      badge.textContent = chatUnreadCount;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }

  // Enter key sends message
  document.getElementById('chatInput').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); sendChatMessage(); }
  });

  document.getElementById('chatNameInput').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); saveChatName(); }
  });

  // Restore chat state from localStorage
  (function () {
    var name = localStorage.getItem('chatName');
    if (name) {
      document.getElementById('chatNameInput').value = name;
      document.getElementById('chatNameForm').style.display = 'none';
      document.getElementById('chatInputArea').style.display = 'flex';
    }
    // Start polling in background to catch admin replies
    startPolling();
  })();
})();
