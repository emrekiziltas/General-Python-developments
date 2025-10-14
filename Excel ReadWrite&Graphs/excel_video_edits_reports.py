# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 14:48:33 2025

@author: ek
"""

import pandas as pd

# Veri seti

file_path = r"C:\Users\ek675\rickandmorty\edits.xlsx"

df = pd.read_excel(file_path, sheet_name="Sheet1")

# Grup haritası
group_map = {
    "OGGW01": "OGGW Series",
    "OGGW02": "OGGW Series",
    "OGGW03": "OGGW Series",
    "BID": "BID Series",
    "BIDW01": "BID Series",
    "TGAW01": "TGAW Series",
    "TGAW02": "TGAW Series",
    "RCL": "RCL Series",
    "RCLW04": "RCL Series",
    "DNMW06": "DNM Series",
    "Public": "Public",
    "Gateway": "Gateway",
    "9th Edwards Symposium": "Gateway"
}

df["Activity Group"] = df["Activity"].map(group_map)

# Özet tablolar
summary_location = df.groupby("Location")["Count"].sum().reset_index()
summary_source = df.groupby("Source")["Count"].sum().reset_index()
summary_activity = df.groupby("Activity")["Count"].sum().reset_index()
grouped_activity_summary = df.groupby("Activity Group")["Count"].sum().reset_index().sort_values(by="Count",
                                                                                                 ascending=False)

# Excel yazımı
with pd.ExcelWriter("Activity_Report_with_Grouped_Activities.xlsx", engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name="Detailed Data", index=False)
    summary_location.to_excel(writer, sheet_name="Summary by Location", index=False)
    summary_source.to_excel(writer, sheet_name="Summary by Source", index=False)
    summary_activity.to_excel(writer, sheet_name="Summary by Activity", index=False)
    grouped_activity_summary.to_excel(writer, sheet_name="Grouped Activity Summary", index=False)

    workbook = writer.book
    worksheet = writer.sheets["Grouped Activity Summary"]

    # Grafik ekleme
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': 'Grouped Activities',
        'categories': ['Grouped Activity Summary', 1, 0, len(grouped_activity_summary), 0],
        'values': ['Grouped Activity Summary', 1, 1, len(grouped_activity_summary), 1],
        'data_labels': {'value': True},
    })
    chart.set_title({'name': 'Total Count by Activity Group'})
    chart.set_x_axis({'name': 'Activity Group'})
    chart.set_y_axis({'name': 'Total Countt'})
    worksheet.insert_chart('D2', chart)

    # Grafik 1: Konuma göre toplam sayılar
    worksheet1 = writer.sheets["Summary by Location"]
    chart1 = workbook.add_chart({'type': 'column'})
    chart1.add_series({
        'name': 'Count by Location',
        'categories': ['Summary by Location', 1, 0, len(summary_location), 0],
        'values': ['Summary by Location', 1, 1, len(summary_location), 1],
        'data_labels': {'value': True},
    })
    chart1.set_title({'name': 'Count by Location'})
    chart1.set_x_axis({'name': 'Location'})
    chart1.set_y_axis({'name': 'Total Count'})
    worksheet1.insert_chart('D2', chart1)

    # Grafik 2: Kaynağa göre dağılım (pasta grafik)
    worksheet2 = writer.sheets["Summary by Source"]
    chart2 = workbook.add_chart({'type': 'pie'})
    chart2.add_series({
        'name': 'Count by Source',
        'categories': ['Summary by Source', 1, 0, len(summary_source), 0],
        'values': ['Summary by Source', 1, 1, len(summary_source), 1],
        'data_labels': {'value': True},
    })
    chart2.set_title({'name': 'Count Distribution by Source'})
    worksheet2.insert_chart('D2', chart2)

    # Grafik 3: Aktivitelere göre toplam sayılar (çubuk grafik)
    worksheet3 = writer.sheets["Summary by Activity"]
    chart3 = workbook.add_chart({'type': 'bar'})
    chart3.add_series({
        'name': 'Activity Counts',
        'categories': ['Summary by Activity', 1, 0, len(summary_activity), 0],
        'values': ['Summary by Activity', 1, 1, len(summary_activity), 1],
        'data_labels': {'value': True},
    })
    chart3.set_title({'name': 'Total Count by Activity'})
    chart3.set_x_axis({'name': 'Activity'})
    chart3.set_y_axis({'name': 'Total Count'})
    worksheet3.insert_chart('D2', chart3)

print("✅ Rapor başarıyla: Activity_Report_with_Grouped_Activities.xlsx")
