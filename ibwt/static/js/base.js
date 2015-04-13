
    $.extend({
        postJSON: function (url, data, callback) {
            return jQuery.post(url, data, callback, "json");
        }
    });
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE') {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRF-Token", $('meta[name=csrf-token]').attr('content'));
                }
            }
        }
    });
$(document).ready(function() {


    Sijax.setRequestUri("/9c189051675bf047a965e835814");

        Metronic.init(); // init metronic core componets
        Layout.init(); // init layout
        QuickSidebar.init() // init quick sidebar
        UIAlertDialogApi.init();


        namespace = '/shoutbox'; // change to an empty string to use the global namespace

        // the socket.io documentation recommends sending an explicit package upon connection
        //  this is specially important when using the global namespace
        socket = io.connect('https://' + document.domain + ':' + location.port + namespace);

        // event handler for server sent data
        // the data is displayed in the "Received" section of the page
        socket.on('send_message_response', function(resp_message) {
            var message = $.parseJSON(resp_message);
            if(message.locale==global_locale) {
                var html_li = '<li><a href="javascript:;" class="online"><span class="chat-user-name">' + message.text + '</span><br><span class="chat-user-msg">' + message.user + '</span></a></li>';
                $(html_li).hide().prependTo('#chat-list-rows').slideDown('fast');
            }
        });
            socket.on('my response', function(msg) {
                $('#log').append('<br>Received #' + msg.count + ': ' + msg.data);
            });

        $('#sendchat').click(function(event) {
            if($.trim($('#broadcast_data').val()) != '') {
                socket.emit('send_message', {data: $('#broadcast_data').val()});
            };
            $('#broadcast_data').val('');
        });

        $('#chat-list-rows').slimScroll({
                height: '450px'
            });

        $('.better-select').selectize({
            sortField: 'text'
        });


        select_currency = $('#select-currency').selectize({
            sortField: 'text'
        });
        select_currency2 = $('#select-currency2').selectize({
            sortField: 'text'
        });

        Sijax.request('get_trade_data')
        Sijax.request('get_latest_buy_orders')
        Sijax.request('get_latest_sell_orders')
        Sijax.request('get_grouped_sell_orders')
        Sijax.request('get_grouped_buy_orders')
        Sijax.request('get_messages_chat')

        //$('.number').number(true, 6);
        $('form #amount_buy, form #amount_sell').keyup();
        $('form#buy_form, form#sell_form').on('submit', function(e) {
            var currentForm = this;
            e.preventDefault();
            bootbox.confirm("Are you sure?", function (result) {
                        if (result) {
                            var btn = $(currentForm).find(':submit');
                            btn.attr('type', 'image');
                            btn.removeClass('btn-success');
                            btn.removeClass('btn-danger');
                            btn.addClass('btn-default');
                            btn.attr('src', '/static/assets/global/img/loading.gif');
                            btn.attr('disabled', 'disabled');
                            $(currentForm).unbind('submit');
                            $(currentForm).on('submit', function () {
                                return false;
                            });
                            currentForm.submit();
                        }
                    }
            );
        });



        /* total calculation */
        $('form #amount_buy, form #price_buy').on('keyup', function(){
            var amount=$('#amount_buy').val();
            var price_per_unit=$('#price_buy').val();
            var form = $(this).closest('form');
            var form_id = form.attr('id');
            if($.isNumeric(amount) && $.isNumeric(price_per_unit)) {
                form.find('.total-order span.value').html('<img src="/static/assets/global/img/loading.gif">');
                form.find('.fee span.value-fee').html('<img src="/static/assets/global/img/loading.gif">');
                Sijax.request('calculate_total', [amount, price_per_unit, form_id]);
            } else {
                form.find('.total-order span.value').html('0');
            }
        })

        /* total calculation */
        $('form #amount_sell, form #price_sell').on('keyup', function(){
            var amount=$('#amount_sell').val();
            var price_per_unit=$('#price_sell').val();
            var form = $(this).closest('form');
            var form_id = form.attr('id');
            if($.isNumeric(amount) && $.isNumeric(price_per_unit)) {
                form.find('.total-order span.value').html('<img src="/static/assets/global/img/loading.gif">');
                form.find('.fee span.value-fee').html('<img src="/static/assets/global/img/loading.gif">');
                Sijax.request('calculate_total', [amount, price_per_unit, form_id]);
            } else {
                form.find('.total-order span.value').html('0');
            }
        })

        get_main_chart()

        $('.main-chart .reload').click(function(){
            get_main_chart()
        })

        $('#latest-buy-orders .reload').click(function(){
            Sijax.request('get_latest_buy_orders')
        })

        $('#latest-sell-orders .reload').click(function(){
            Sijax.request('get_latest_sell_orders')
        })

        $('#grouped-sell-orders .reload').click(function(){
            Sijax.request('get_grouped_sell_orders')
        })

        $('#grouped-buy-orders .reload').click(function(){
            Sijax.request('get_grouped_buy_orders')
        })

        $('#trade-btn').click(function(){
            var currency = $('#select-currency').val();
            var currency2 = $('#select-currency2').val();
            if ($.trim(currency) != '' && $.trim(currency2) != '') {
                window.location.href='/trade/'+currency+'/'+currency2;
            }
        })




    })

    function render_grouped_sell_orders(data) {
        var ref = '#grouped-sell-orders';
        $(ref).html(data.html);
        data_tabelize(ref)
    }

    function render_grouped_buy_orders(data) {
        var ref = '#grouped-buy-orders';
        $(ref).html(data.html);
        data_tabelize(ref)
    }
    function render_latest_sell_orders(data) {
        var ref = '#latest-sell-orders';
        $(ref).html(data.html);
        data_tabelize(ref)
    }

    function render_latest_buy_orders(data) {
        var ref = '#latest-buy-orders';
        $(ref).html(data.html);
        data_tabelize(ref)
    }

    function render_trade_data(data) {
        $('#highest-bid-price').html(data.max_sell_price);
        $('#lowest-bid-price').html(data.min_buy_price);
        $('#currency-volume').html(data.currency_volume);
        $('#currency2-volume').html(data.currency2_volume);

        if($.trim($('#buy_form #price_buy').val()) == 0 || $.trim($('#buy_form #price_buy').val()) == '') {
            $('#buy_form #price_buy').val(data.min_buy_price_raw);
        }

        if($.trim($('#sell_form #price_sell').val()) == 0 || $.trim($('#sell_form #price_sell').val()) == '') {
            $('#sell_form #price_sell').val(data.max_sell_price_raw);
        }

    }


    function render_fee_total(data) {
        $('#'+data.form_id+' .fee span.value-fee').html(data.fee);
        $('#'+data.form_id+' .total-order span.value').html(data.total_order);
    }

    function data_tabelize(reference) {
        if($(reference).length) {
            var dTable = $(reference + ' table').DataTable({
                "dom": 'T<"clear">C<"clear">lfrtip<"clear">',
                "deferRender": true,
                tableTools: {
                    "sSwfPath": "/static/assets/global/swf/copy_csv_xls_pdf.swf"
                },
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/" + global_locale_en +".json"
                },
                "aaSorting": []


            });
        }
    }

    function get_main_chart() {
        $.postJSON('/chart.json', function (resp) {
            var data = resp.result;
            // split the data set into ohlc and volume
            var ohlc = [],
                    volume = [],
                    dataLength = data.length,
            // set the allowed units for data grouping
                    groupingUnits = [[
                        'week',                         // unit name
                        [1]                             // allowed multiples
                    ], [
                        'month',
                        [1, 2, 3, 4, 6]
                    ]],

                    i = 0;
            data = data.sort(function (a, b) {
                return a[0] - b[0];
            })
            for (i; i < dataLength; i += 1) {
                ohlc.push([
                    data[i][0], // the date
                    data[i][1], // open
                    data[i][2], // high
                    data[i][3], // low
                    data[i][4] // close
                ]);

                volume.push([
                    data[i][0], // the date
                    data[i][5] // the volume
                ]);
            }


            // create the chart
            $('#chart').highcharts('StockChart', {

                global: {
                    /**
                     * Use moment-timezone.js to return the timezone offset for individual
                     * timestamps, used in the X axis labels and the tooltip header.
                     */
                    getTimezoneOffset: function (timestamp) {
                        var zone = timezone,
                                timezoneOffset = moment.tz.zone(zone).parse(timestamp);

                        return timezoneOffset;
                    }
                },

                rangeSelector: {
                    buttons: [{
                        type: 'minute',
                        count: 5,
                        text: '5m.'
                    }, {
                        type: 'minute',
                        count: 30,
                        text: '30m.'
                    },
                        {
                            type: 'hour',
                            count: 1,
                            text: '1h'
                        }, {
                            type: 'day',
                            count: 1,
                            text: '1D'
                        }, {
                            type: 'week',
                            count: 1,
                            text: '1W'
                        }, {
                            type: 'month',
                            count: 1,
                            text: '1M'
                        }, {
                            type: 'year',
                            count: 1,
                            text: '1Y'
                        },
                        {
                            type: 'all',
                            count: 1,
                            text: 'All'
                        }],
                    selected: 5,
                    inputEnabled: true
                },
                xAxis: {
                    type: 'datetime'
                },

                yAxis: [{
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'OHLC'
                    },
                    height: '60%',
                    lineWidth: 2
                }, {
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    title: {
                        text: 'Volume'
                    },
                    top: '65%',
                    height: '35%',
                    offset: 0,
                    lineWidth: 2
                }],
                credits: {
                    enabled: false
                },
                series: [{
                    type: 'candlestick',
                    name: graph_name,
                    data: ohlc,
                    dataGrouping: {
                        units: groupingUnits
                    }
                }, {
                    type: 'column',
                    name: 'Volume',
                    data: volume,
                    yAxis: 1,
                    dataGrouping: {
                        units: groupingUnits
                    }
                }]
            });
        });
    }

    function render_chat_messages(data) {
        var ref = '#chat-list-rows';
        $('.chat-loading').hide()
        $(ref).append(data.html);
    }