// 筛选模块
const filters = {
    level1: new Set(),
    level2: new Set(),
    style: new Set(),
    stocks: new Set(),
    level1ForLevel2: 'all'
};

// 更新下拉框选项
function updateSelectOptions(selectId, options) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    select.innerHTML = '<option value="all" selected>全部显示</option>';
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        select.appendChild(option);
    });
}

// 更新一级行业下拉框（用于二级筛选）
function updateLevel1ForLevel2Select(level1List) {
    const select = document.getElementById('filterLevel1ForLevel2');
    if (!select) return;
    
    select.innerHTML = '<option value="all">全部一级行业</option>';
    level1List.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        select.appendChild(option);
    });
}

// 更新二级行业下拉框
function updateLevel2SelectOptions(level2List, selectedLevel1) {
    const select = document.getElementById('filterLevel2');
    if (!select) return;
    
    const filtered = selectedLevel1 === 'all' 
        ? level2List 
        : level2List.filter(item => item.level1 === selectedLevel1);
    
    select.innerHTML = '<option value="all" selected>全部显示</option>';
    filtered.forEach(item => {
        const option = document.createElement('option');
        option.value = item.name;
        option.textContent = item.name;
        select.appendChild(option);
    });
}

// 更新统计卡片
function updateStats(data) {
    document.getElementById('totalAsset').textContent = 
        data.totalAsset.toLocaleString() + ' 元';
    document.getElementById('positionCount').textContent = 
        new Set(data.positions.map(p => p.symbol)).size;
    document.getElementById('level1Count').textContent = data.level1List.length;
    document.getElementById('styleCount').textContent = data.styleList.length;
}

// 重置所有筛选
function resetAllFilters() {
    filters.level1.clear();
    filters.level2.clear();
    filters.style.clear();
    filters.stocks.clear();
    filters.level1ForLevel2 = 'all';
    
    // 重置下拉框
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.id !== 'filterLevel1ForLevel2') {
            select.value = ['all'];
        } else {
            select.value = 'all';
        }
    });
}