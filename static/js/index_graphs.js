    getData();

    function getData() {
        $.get("/ajax/get_host_stats", function(resp) {
            memory = resp['memory']
            cpu = resp['cpu']
            dates = resp['dates']
            iowait = resp['iowait']
            max_memory = resp['max_memory'][0]

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
            max: max_memory,
            title: {
                text: 'Memory Used (MB)'
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
            enabled:false
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'Memory (MB)',
            data: memory,
            type: 'area',
            color: '#FFA161'
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
            enabled:false
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'CPU (%)',
            data: cpu,
            type: 'area',
            color: '#FFA161'
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
            enabled:false 
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'IOWait (%)',
            data: iowait,
            type: 'area',
            color: '#FFA161'
        }]
    });
    };
