// 图表渲染模块
const charts = {};

// 初始化图表
function initChart(containerId) {
    if (!charts[containerId]) {
        const element = document.getElementById(containerId);
        if (element) {
            charts[containerId] = echarts.init(element);
        }
    }
    return charts[containerId];
}

// 渲染饼图
function renderPieChart(containerId, title, data) {
    const chart = initChart(containerId);
    if (!chart) return;
    
    const option = {
        title: {
            text: title,
            left: 'center',
            top: 10,
            textStyle: { fontSize: 14, color: '#334155' }
        },
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c}% ({d}%)'
        },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '55%'],
            data: data.length > 0 ? data : [{ name: '无数据', value: 100 }],
            itemStyle: {
                borderRadius: 8,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: { show: false },
            emphasis: {
                scale: true,
                label: { show: true }
            }
        }]
    };
    
    chart.setOption(option);
    chart.resize();
}

// 渲染对比柱状图（实际 vs 预期）- 支持偏差阈值筛选
function renderComparisonChart(containerId, title, data, threshold = 0) {
    const chart = initChart(containerId);
    if (!chart) return;
    
    // 根据阈值筛选数据（偏差绝对值大于阈值的才显示）
    let filteredData = data;
    if (threshold > 0) {
        filteredData = data.filter(item => Math.abs(item.actual - item.expected) >= threshold);
    }
    
    if (filteredData.length === 0) {
        // 无数据显示提示
        const option = {
            title: {
                text: title,
                left: 'center',
                top: 10,
                textStyle: { fontSize: 14, color: '#334155' }
            },
            graphic: {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '无符合条件的行业数据\n（偏差均小于阈值）',
                    fill: '#999',
                    fontSize: 14,
                    lineWidth: 0
                }
            }
        };
        chart.setOption(option);
        return;
    }
    
    const categories = filteredData.map(item => item.name);
    const actualData = filteredData.map(item => item.actual);
    const expectedData = filteredData.map(item => item.expected);
    
    const option = {
        title: {
            text: title,
            left: 'center',
            top: 10,
            textStyle: { fontSize: 14, color: '#334155' }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function(params) {
                let result = params[0].axisValue + '<br/>';
                params.forEach(p => {
                    result += `${p.marker} ${p.seriesName}: ${p.value}%<br/>`;
                });
                return result;
            }
        },
        legend: {
            data: ['实际仓位', '预期仓位'],
            left: 'left',
            top: 30,  // 调整位置，避免遮挡
            itemWidth: 25,
            itemHeight: 14
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '8%',  // 增加底部空间
            top: '15%',    // 增加顶部空间给图例
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: categories,
            axisLabel: {
                rotate: categories.length > 8 ? 45 : 0,
                interval: 0,
                fontSize: 11
            }
        },
        yAxis: {
            type: 'value',
            name: '仓位 (%)',
            nameLocation: 'middle',
            nameGap: 40
        },
        series: [
            {
                name: '实际仓位',
                type: 'bar',
                data: actualData,
                itemStyle: {
                    color: '#3b82f6',
                    borderRadius: [4, 4, 0, 0]
                },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}%',
                    fontSize: 11
                }
            },
            {
                name: '预期仓位',
                type: 'bar',
                data: expectedData,
                itemStyle: {
                    color: '#10b981',
                    borderRadius: [4, 4, 0, 0]
                },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}%',
                    fontSize: 11
                }
            }
        ]
    };
    
    chart.setOption(option);
    chart.resize();
}

// 聚合数据
function aggregateData(items, groupKey, valueKey = 'position_pct') {
    const map = new Map();
    items.forEach(item => {
        const key = item[groupKey];
        if (!key) return;
        map.set(key, (map.get(key) || 0) + (item[valueKey] || 0));
    });
    
    return Array.from(map.entries())
        .map(([name, value]) => ({ 
            name, 
            value: Math.round(value * 10) / 10 
        }))
        .sort((a, b) => b.value - a.value);
}

// 重绘所有图表
function refreshCharts(data, filters) {
    if (!data) return;

    // 一级行业
    const level1Data = aggregateData(
        filterData(data.positions, 'level1', filters.level1), 
        'level1_name'
    );
    renderPieChart('chartLevel1', '一级行业分布', level1Data);
    
    // 一级行业对比图（使用偏差阈值）
    if (data.level1ExpectedList && data.level1ExpectedList.length > 0) {
        const threshold = window.biasThreshold || 0;
        renderComparisonChart('chartLevel1Compare', '一级行业 · 实际 vs 预期', data.level1ExpectedList, threshold);
    }

    // 二级行业
    const level2Data = aggregateData(
        filterLevel2Data(data.positions, filters), 
        'level2_name'
    );
    renderPieChart('chartLevel2', '二级行业分布', level2Data);
    
    // 二级行业对比图（根据一级行业筛选）
    let level2CompareData = data.level2ExpectedList || [];
    if (filters.level1ForLevel2 !== 'all') {
        level2CompareData = level2CompareData.filter(item => item.level1 === filters.level1ForLevel2);
    }
    if (level2CompareData.length > 0) {
        const threshold = window.biasThreshold || 0;
        renderComparisonChart('chartLevel2Compare', '二级行业 · 实际 vs 预期', level2CompareData, threshold);
    }

    // 风格
    const styleData = aggregateData(
        filterData(data.positions, 'style', filters.style), 
        'style'
    );
    renderPieChart('chartStyle', '风格分布', styleData);

    // 具体标的
    const totalStockValue = data.positions.reduce((sum, item) => sum + (item.industry_value || 0), 0);
    const cashValue = data.totalAsset - totalStockValue;
    const cashPct = cashValue > 0 ? (cashValue * 100 / data.totalAsset) : 0;

    let stockData = aggregateData(
        filterData(data.positions, 'stocks', filters.stocks), 
        'name'
    );

    if (cashPct > 0.01) {
        stockData.push({ name: '现金', value: Math.round(cashPct * 10) / 10 });
        stockData.sort((a, b) => b.value - a.value);
    }

    stockData = stockData.slice(0, 15);
    renderPieChart('chartStocks', '具体标的分布', stockData);  
}

// 筛选数据
function filterData(positions, filterType, selectedItems) {
    if (selectedItems.size === 0) return positions;
    return positions.filter(item => {
        switch(filterType) {
            case 'level1': return selectedItems.has(item.level1_name);
            case 'style': return selectedItems.has(item.style);
            case 'stocks': return selectedItems.has(item.name);
            default: return true;
        }
    });
}

// 筛选二级行业数据
function filterLevel2Data(positions, filters) {
    let filtered = positions;
    
    if (filters.level1ForLevel2 !== 'all') {
        filtered = filtered.filter(item => item.level1_name === filters.level1ForLevel2);
    }
    
    if (filters.level2.size > 0) {
        filtered = filtered.filter(item => filters.level2.has(item.level2_name));
    }
    
    return filtered;
}