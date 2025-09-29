export const exportCSV = (rows: any[], filename = 'export.csv') => {
    if (!rows || rows.length === 0) return
    const header = Object.keys(rows[0])
    const csv = [header.join(','), ...rows.map(r => header.map(h => `"${String(r[h] || '')}"`).join(','))].join('')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
}