$(() => {
    $('.filter').keypress(function (event) {
        if (event.which == 13) {
            document.location.search = 'filter=' + encodeURIComponent($('.filter').val());
        }
    });

    $('.conversation-id').on('click', function (event) {
        $('.conversation-id').removeClass('active');
        $(this).addClass('active');
        const [time, port1, port2] = $(this).text().split(' ');
        $.getJSON('/conversation/' + [time, port1, port2].join('-'), function (data) {
            $('.view').empty()
            data['conversation'].forEach((message) => {
                const [src, dst, msg] = message;
                const card = $('' +
                               '<div class="card">' +
                               '<h5 class="card-header"></h5>' +
                               '<div class="card-body">' +
                               '<pre class="card-text"></pre>' +
                               '</div>' +
                               '</div>'
                              );
                card.find('h5').text(src + ' → ' + dst);
                card.find('pre').text(msg);
                card.find('.card-body').css('background-color', src == port1 ? 'rgba(255, 0, 0, 0.1)' : 'rgba(0, 0, 255, 0.1)');
                card.appendTo('.view');
            });
        });
    });
});
