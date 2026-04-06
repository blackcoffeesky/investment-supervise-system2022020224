// 数据库操作模块
let db = null;
let SQL = null;

// 初始化SQL.js
async function initSQL() {
    try {
        SQL = await initSqlJs({
            locateFile: file =>
                `https://cdn.jsdelivr.net/npm/sql.js@1.8.0/dist/${file}`
        });

        console.log("SQL.js 初始化成功");
        return SQL;

    } catch (err) {
        console.error("SQL.js 初始化失败:", err);
        throw err;
    }
}

// 加载数据库文件
async function loadDatabase(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const uint8Array = new Uint8Array(e.target.result);
                db = new SQL.Database(uint8Array);
                resolve(db);
            } catch (err) {
                reject(err);
            }
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

// 获取预期仓位数据
function getExpectedPositions() {
    if (!db) return { level1: [], level2: [] };
    
    try {
        // 获取一级行业预期仓位
        const level1Result = db.exec("SELECT id, name, expected_position FROM industry_level1 ORDER BY name");
        const level1List = level1Result.length > 0 ? level1Result[0].values.map(row => ({
            id: row[0],
            name: row[1],
            expected_position: row[2] || 0
        })) : [];
        
        // 获取二级行业预期仓位
        const level2Result = db.exec(`
            SELECT l2.id, l2.name, l2.expected_position, l1.name as level1_name
            FROM industry_level2 l2 
            JOIN industry_level1 l1 ON l2.level1_id = l1.id 
            ORDER BY l1.name, l2.name
        `);
        const level2List = level2Result.length > 0 ? level2Result[0].values.map(row => ({
            id: row[0],
            name: row[1],
            expected_position: row[2] || 0,
            level1_name: row[3]
        })) : [];
        
        return { level1: level1List, level2: level2List };
        
    } catch (e) {
        console.error('获取预期仓位失败:', e);
        return { level1: [], level2: [] };
    }
}

// 更新一级行业预期仓位
function updateLevel1ExpectedPosition(id, expectedPosition) {
    if (!db) return false;
    
    try {
        db.run(`UPDATE industry_level1 SET expected_position = ? WHERE id = ?`, [expectedPosition, id]);
        console.log(`更新一级行业 ${id} 预期仓位为 ${expectedPosition}`);
        return true;
    } catch (e) {
        console.error('更新一级行业预期仓位失败:', e);
        return false;
    }
}

// 更新二级行业预期仓位
function updateLevel2ExpectedPosition(id, expectedPosition) {
    if (!db) return false;
    
    try {
        db.run(`UPDATE industry_level2 SET expected_position = ? WHERE id = ?`, [expectedPosition, id]);
        console.log(`更新二级行业 ${id} 预期仓位为 ${expectedPosition}`);
        return true;
    } catch (e) {
        console.error('更新二级行业预期仓位失败:', e);
        return false;
    }
}

// 查询数据（增强版，包含预期仓位）
function queryData() {
    if (!db) return null;

    try {
        // 获取现金
        const accountResult = db.exec("SELECT cash FROM account ORDER BY date DESC LIMIT 1");
        const cash = accountResult.length > 0 ? accountResult[0].values[0][0] : 0;
        console.log("当前现金:", cash);
        
        // 第一步：获取所有持仓股票的基础信息（去重）
        const stockQuery = `
            SELECT
                ss.symbol,
                ss.name,
                ss.is_index,
                sp.amount,
                sp.vwap,
                ss.style_id,
                sc.style
            FROM stock_position sp
            JOIN stock_static ss ON sp.symbol = ss.symbol
            LEFT JOIN style_category sc ON ss.style_id = sc.id
        `;
        
        const stockResult = db.exec(stockQuery);
        const stockMap = new Map(); // 用 symbol 去重
        if (stockResult.length > 0) {
            const stockColumns = stockResult[0].columns;
            const stockRows = stockResult[0].values;
            
            stockRows.forEach(row => {
                const stock = {};
                stockColumns.forEach((col, idx) => {
                    stock[col] = row[idx];
                });
                
                stock.market_value = stock.amount;
                stockMap.set(stock.symbol, stock);
            });
        }

        // 第二步：获取行业关联（可能有多个）
        const industryQuery = `
            SELECT 
                il.symbol,
                il.level2_id,
                il.weight,
                l2.name as level2_name,
                l1.name as level1_name,
                l1.id as level1_id,
                l2.id as level2_id,
                l1.expected_position as level1_expected,
                l2.expected_position as level2_expected
            FROM industry_level il
            JOIN industry_level2 l2 ON il.level2_id = l2.id
            JOIN industry_level1 l1 ON l2.level1_id = l1.id
        `;
        
        const industryResult = db.exec(industryQuery);
        const industryMap = new Map(); // symbol -> 行业数组
        
        if (industryResult.length > 0) {
            const indColumns = industryResult[0].columns;
            const indRows = industryResult[0].values;
            
            indRows.forEach(row => {
                const ind = {};
                indColumns.forEach((col, idx) => {
                    ind[col] = row[idx];
                });
                
                if (!industryMap.has(ind.symbol)) {
                    industryMap.set(ind.symbol, []);
                }
                industryMap.get(ind.symbol).push({
                    level1_name: ind.level1_name,
                    level2_name: ind.level2_name,
                    level1_id: ind.level1_id,
                    level2_id: ind.level2_id,
                    level1_expected: ind.level1_expected || 0,
                    level2_expected: ind.level2_expected || 0,
                    weight: ind.weight || 100
                });
            });
        }

        // 第三步：构建 positions 数组（按行业拆分）
        const positions = [];
        let totalStockValue = 0;
        stockMap.forEach(stock => {
            totalStockValue += stock.market_value;
        });
        
        const totalAsset = cash + totalStockValue;
        
        // 收集行业实际仓位（用于预期仓位对比）
        const level1ActualMap = new Map();
        const level2ActualMap = new Map();
        
        stockMap.forEach(stock => {
            const industries = industryMap.get(stock.symbol) || [];
            
            if (industries.length === 0) {
                positions.push({
                    symbol: stock.symbol,
                    name: stock.name,
                    amount: stock.amount,
                    market_value: stock.market_value,
                    industry_value: stock.market_value,
                    position_pct: totalAsset > 0 ? stock.market_value * 100 / totalAsset : 0,
                    style: stock.style,
                    style_id: stock.style_id,
                    is_index: stock.is_index,
                    level1_name: '未分类',
                    level2_name: '未分类',
                    weight: 100
                });
            } else {
                industries.forEach(ind => {
                    const industryValue = stock.market_value * (ind.weight / 100);
                    const positionPct = totalAsset > 0 ? industryValue * 100 / totalAsset : 0;
                    
                    positions.push({
                        symbol: stock.symbol,
                        name: stock.name,
                        amount: stock.amount,
                        market_value: stock.market_value,
                        industry_value: industryValue,
                        position_pct: positionPct,
                        style: stock.style,
                        style_id: stock.style_id,
                        is_index: stock.is_index,
                        level1_name: ind.level1_name,
                        level2_name: ind.level2_name,
                        level1_id: ind.level1_id,
                        level2_id: ind.level2_id,
                        weight: ind.weight
                    });
                    
                    // 累加实际仓位
                    level1ActualMap.set(ind.level1_name, (level1ActualMap.get(ind.level1_name) || 0) + positionPct);
                    level2ActualMap.set(ind.level2_name, (level2ActualMap.get(ind.level2_name) || 0) + positionPct);
                });
            }
        });

        // 获取预期仓位数据
        const expectedPositions = getExpectedPositions();
        
        // 构建一级行业预期仓位映射 
        const level1ExpectedMap = new Map();
        expectedPositions.level1.forEach(item => {
            level1ExpectedMap.set(item.name, item.expected_position);
        });
        
        // 构建二级行业预期仓位映射 
        const level2ExpectedMap = new Map();
        expectedPositions.level2.forEach(item => {
            level2ExpectedMap.set(item.name, item.expected_position);
        });
        
        // 获取完整的一级行业列表（包含预期仓位）
        const level1FullList = expectedPositions.level1.map(item => ({
            name: item.name,
            expected: item.expected_position,
            actual: level1ActualMap.get(item.name) || 0
        }));
        
        // 获取完整的二级行业列表（包含预期仓位）
        const level2FullList = expectedPositions.level2.map(item => ({
            name: item.name,
            level1: item.level1_name,
            expected: item.expected_position,
            actual: level2ActualMap.get(item.name) || 0
        }));
        
        // 获取风格列表
        const styleResult = db.exec("SELECT style FROM style_category ORDER BY style");
        const styleList = styleResult.length > 0 ? styleResult[0].values.map(row => row[0]) : [];
        
        // 获取标的列表
        const stockList = Array.from(stockMap.values()).map(s => s.name).sort();

        return {
            totalAsset,
            positions,
            level1List: level1FullList.map(l => l.name),
            level2List: level2FullList.map(l => ({ name: l.name, level1: l.level1 })),
            styleList,
            stockList,
            level1ExpectedList: level1FullList,
            level2ExpectedList: level2FullList
        };

    } catch (e) {
        console.error('查询失败:', e);
        return null;
    }
}

// 导出数据库（用于保存修改）
function exportDatabase() {
    if (!db) return null;
    return db.export();
}

// 下载数据库文件
function downloadDatabase() {
    const data = exportDatabase();
    if (!data) return;
    
    const blob = new Blob([data], { type: 'application/x-sqlite3' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'portfolio_updated.db';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}