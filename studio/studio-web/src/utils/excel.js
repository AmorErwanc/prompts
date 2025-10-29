import * as XLSX from 'xlsx'

/**
 * 读取 Excel 文件并转换为 JSON 数据
 * @param {File} file - Excel 文件对象
 * @returns {Promise<Array>} - 返回数据数组
 */
export function readExcel(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })

        // 读取第一个 sheet
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]

        // 转换为 JSON，第一行作为表头
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })

        // 第一行是参数名称
        const headers = jsonData[0]

        // 后续行是数据
        const rows = jsonData.slice(1).map(row => {
          const obj = {}
          headers.forEach((header, index) => {
            obj[header] = row[index] || ''
          })
          return obj
        })

        resolve({ headers, rows })
      } catch (error) {
        reject(error)
      }
    }

    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }

    reader.readAsArrayBuffer(file)
  })
}

/**
 * 导出数据为 Excel 文件
 * @param {Array} data - 要导出的数据
 * @param {String} fileName - 文件名
 */
export function exportExcel(data, fileName = '测试结果.xlsx') {
  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')
  XLSX.writeFile(workbook, fileName)
}
