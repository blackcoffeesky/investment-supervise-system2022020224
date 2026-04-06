// 主逻辑模块
let currentData = null;

// 初始化
window.addEventListener('DOMContentLoaded', async function() {
    await initSQL();
    setupEventListeners();
    
    // 初始化时禁用加载按钮
    document.getElementById('loadBtn').disabled = true;
});

// 设置事件监听
function setupEventListeners() {
    // 文件选择
    document.getElementById('dbFile').addEventListener('change', function(e) {
        const file = e.target.files[0];
        const fileNameSpan = document.getElementById('fileName');
        const loadBtn = document.getElementById('loadBtn');
        const dbStatus = document.getElementById('dbStatus');
        
        if (file) {
            fileNameSpan.textContent = file.name;
            loadBtn.disabled = false;
            dbStatus.innerHTML = '<i class="fas fa-check-circle" style="color:#10b981;"></i> 已选择: ' + file.name;
        } else {
            fileNameSpan.textContent = '选择数据库文件 (.db)';
            loadBtn.disabled = true;
            dbStatus.innerHTML = '<i class="fas fa-info-circle"></i> 未连接';
        }
    });

    // 加载数据
    document.getElementById('loadBtn').addEventListener('click', async function() {
        const fileInput = document.getElementById('dbFile');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('请先选择数据库文件');
            return;
        }

        const btn = this;
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 加载中...';
        
        const dbStatus = document.getElementById('dbStatus');
        dbStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 加载中';

        try {
            await loadDatabase(file);
            const data = queryData();
            
            if (data && data.positions && data.positions.length > 0) {
                currentData = data;
                
                updateStats(data);
                updateSelectOptions('filterLevel1', data.level1List);
                updateSelectOptions('filterStyle', data.styleList);
                updateSelectOptions('filterStocks', data.stockList);
                updateLevel1ForLevel2Select(data.level1List);
                updateLevel2SelectOptions(data.level2List, 'all');
                
                resetAllFilters();
                refreshCharts(data, filters);
                
                // 初始化预期仓位编辑面板
                initExpectedPositionEditors(data);
                
                dbStatus.innerHTML = '<i class="fas fa-check-circle" style="color:#10b981;"></i> 已连接';
            } else {
                throw new Error('数据库中没有持仓数据或数据格式错误');
            }
        } catch (err) {
            console.error('加载失败:', err);
            dbStatus.innerHTML = '<i class="fas fa-exclamation-triangle" style="color:#ef4444;"></i> 加载失败: ' + err.message;
            alert('加载失败: ' + err.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    });

    // 偏差阈值控制
    const thresholdInput = document.getElementById('biasThreshold');
    if (thresholdInput) {
        thresholdInput.addEventListener('change', function(e) {
            window.biasThreshold = parseFloat(this.value) || 0;
            if (currentData) {
                refreshCharts(currentData, filters);
            }
        });
        // 初始化阈值
        window.biasThreshold = parseFloat(thresholdInput.value) || 0;
    }
    // Tab切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            this.classList.add('active');
            const tabId = this.dataset.tab;
            document.getElementById(`tab-${tabId}`).classList.add('active');
            
            const chartId = `chart${tabId.charAt(0).toUpperCase() + tabId.slice(1)}`;
            if (charts[chartId]) {
                setTimeout(() => charts[chartId].resize(), 100);
            }
        });
    });

    // 一级行业筛选
    document.getElementById('filterLevel1').addEventListener('change', function(e) {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        filters.level1.clear();
        if (!selected.includes('all')) {
            selected.forEach(item => filters.level1.add(item));
        }
        if (currentData) refreshCharts(currentData, filters);
    });

    document.getElementById('resetLevel1').addEventListener('click', function() {
        document.getElementById('filterLevel1').value = ['all'];
        filters.level1.clear();
        if (currentData) refreshCharts(currentData, filters);
    });

    // 二级行业筛选联动
    document.getElementById('filterLevel1ForLevel2').addEventListener('change', function(e) {
        filters.level1ForLevel2 = this.value;
        if (currentData) {
            updateLevel2SelectOptions(currentData.level2List, filters.level1ForLevel2);
            filters.level2.clear();
            refreshCharts(currentData, filters);
        }
    });

    document.getElementById('filterLevel2').addEventListener('change', function(e) {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        filters.level2.clear();
        if (!selected.includes('all')) {
            selected.forEach(item => filters.level2.add(item));
        }
        if (currentData) refreshCharts(currentData, filters);
    });

    document.getElementById('resetLevel2').addEventListener('click', function() {
        document.getElementById('filterLevel1ForLevel2').value = 'all';
        document.getElementById('filterLevel2').value = ['all'];
        filters.level1ForLevel2 = 'all';
        filters.level2.clear();
        if (currentData) {
            updateLevel2SelectOptions(currentData.level2List, 'all');
            refreshCharts(currentData, filters);
        }
    });

    // 风格筛选
    document.getElementById('filterStyle').addEventListener('change', function(e) {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        filters.style.clear();
        if (!selected.includes('all')) {
            selected.forEach(item => filters.style.add(item));
        }
        if (currentData) refreshCharts(currentData, filters);
    });

    document.getElementById('resetStyle').addEventListener('click', function() {
        document.getElementById('filterStyle').value = ['all'];
        filters.style.clear();
        if (currentData) refreshCharts(currentData, filters);
    });

    // 具体标的筛选
    document.getElementById('filterStocks').addEventListener('change', function(e) {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        filters.stocks.clear();
        if (!selected.includes('all')) {
            selected.forEach(item => filters.stocks.add(item));
        }
        if (currentData) refreshCharts(currentData, filters);
    });

    document.getElementById('resetStocks').addEventListener('click', function() {
        document.getElementById('filterStocks').value = ['all'];
        filters.stocks.clear();
        if (currentData) refreshCharts(currentData, filters);
    });
    
    // 保存数据库按钮
    document.getElementById('saveDbBtn').addEventListener('click', function() {
        downloadDatabase();
        alert('数据库已导出保存！');
    });
}

// 初始化预期仓位编辑面板
function initExpectedPositionEditors(data) {
    // 一级行业编辑面板
    const level1Container = document.getElementById('level1ExpectedEditor');
    if (level1Container && data.level1ExpectedList) {
        level1Container.innerHTML = '<h4 style="margin-bottom:12px;"><i class="fas fa-chart-line"></i> 一级行业预期仓位 (%)</h4>';
        data.level1ExpectedList.forEach(item => {
            const editorDiv = document.createElement('div');
            editorDiv.className = 'expected-editor-item';
            editorDiv.innerHTML = `
                <label>${item.name}</label>
                <div class="editor-controls">
                    <input type="number" step="0.1" value="${item.expected}" data-type="level1" data-name="${item.name}" class="expected-input">
                    <span class="actual-hint">当前: ${item.actual.toFixed(1)}%</span>
                </div>
            `;
            level1Container.appendChild(editorDiv);
        });
        
        // 绑定一级行业输入事件
        level1Container.querySelectorAll('.expected-input').forEach(input => {
            input.addEventListener('change', function(e) {
                const value = parseFloat(this.value);
                if (isNaN(value)) return;
                const name = this.dataset.name;
                // 查找对应的行业ID
                const industry = data.level1ExpectedList.find(i => i.name === name);
                if (industry && industry.id !== undefined) {
                    updateLevel1ExpectedPosition(industry.id, value);
                    // 重新加载数据并刷新
                    reloadAndRefresh();
                } else {
                    alert('无法获取行业ID，请确保数据库中有id字段');
                }
            });
        });
    }
    
    // 二级行业编辑面板
    const level2Container = document.getElementById('level2ExpectedEditor');
    if (level2Container && data.level2ExpectedList) {
        level2Container.innerHTML = '<h4 style="margin-bottom:12px;"><i class="fas fa-chart-line"></i> 二级行业预期仓位 (%)</h4>';
        // 按一级行业分组显示
        const grouped = {};
        data.level2ExpectedList.forEach(item => {
            if (!grouped[item.level1]) grouped[item.level1] = [];
            grouped[item.level1].push(item);
        });
        
        for (const [level1, items] of Object.entries(grouped)) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'expected-group';
            groupDiv.innerHTML = `<div class="group-title">${level1}</div>`;
            items.forEach(item => {
                const editorDiv = document.createElement('div');
                editorDiv.className = 'expected-editor-item';
                editorDiv.innerHTML = `
                    <label style="padding-left:16px;">${item.name}</label>
                    <div class="editor-controls">
                        <input type="number" step="0.1" value="${item.expected}" data-type="level2" data-name="${item.name}" data-id="${item.id}" class="expected-input">
                        <span class="actual-hint">当前: ${item.actual.toFixed(1)}%</span>
                    </div>
                `;
                groupDiv.appendChild(editorDiv);
            });
            level2Container.appendChild(groupDiv);
        }
        
        // 绑定二级行业输入事件
        level2Container.querySelectorAll('.expected-input').forEach(input => {
            input.addEventListener('change', function(e) {
                const value = parseFloat(this.value);
                if (isNaN(value)) return;
                const id = parseInt(this.dataset.id);
                if (id) {
                    updateLevel2ExpectedPosition(id, value);
                    reloadAndRefresh();
                } else {
                    alert('无法获取行业ID');
                }
            });
        });
    }
}

// 重新加载数据并刷新界面
function reloadAndRefresh() {
    if (!db) return;
    
    const newData = queryData();
    if (newData) {
        currentData = newData;
        updateStats(newData);
        refreshCharts(newData, filters);
        initExpectedPositionEditors(newData);
    }
}