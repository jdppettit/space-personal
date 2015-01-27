    getData();

    function getData() {
        $.get("http://pluto.pettitservers.com:10051/ajax/get_host_stats", function(resp) {
            memory = resp['memory']
            cpu = resp['cpu']
            dates = resp['dates']
            iowait = resp['iowait']
            
            makeMemory();
            makeCPU();
            makeIOwait();
        });
    };

    function makeMemory() {
       $('#memory').highcharts({
        title: {
            text: ""
        },
        yAxis: {
            title: {
                text: 'Memory Free (MB)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: 'MB'
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'Memory (MB)',
            data: memory,
            type: 'area'
        }]
    }); 
    };

    function makeCPU() {
       $('#cpu').highcharts({
        title: {
            text: ""
        },
        yAxis: {
            max: 100,
            title: {
                text: 'CPU Used (%)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: '%'
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'CPU (%)',
            data: cpu,
            type: 'area'
        }]
    });
    };

    function makeIOwait() {
       $('#iowait').highcharts({
        title: {
            text: ""
        },
        yAxis: {
            max: 100,
            title: {
                text: 'IOWait (%)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: '%'
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'IOWait (%)',
            data: iowait,
            type: 'area'
        }]
    });
    };
