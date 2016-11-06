import QtQuick 2.6
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3

Item {
    width: 640
    height: 320


    RowLayout {
        id: hbox
        spacing: 5
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.fill: parent
        
        Image {
            id: canvas_mpl
            width: 480
            height: 320
            Layout.fillHeight: true
            Layout.fillWidth: true
            fillMode: Image.PreserveAspectFit
            source: "image://mplFigure/figure"
            cache: false
        }
        
        Connections {
            target: draw_mpl
            onStateChanged: {
                canvas_mpl.source = "image://mplFigure/figure?" + Math.random()
                // change URL to refresh image. Add random URL part to avoid caching
            }
            onXFromChanged: {
                canvas_mpl.source = "image://mplFigure/figure?" + Math.random()
            }
            onXToChanged: {
                canvas_mpl.source = "image://mplFigure/figure?" + Math.random()
            }
            onLegendChanged: {
                canvas_mpl.source = "image://mplFigure/figure?" + Math.random()
            }
        }
        
        Connections {
            target: dataModel
            onDataChanged: {
                draw_mpl.update_figure()
            }
        }

        Rectangle {
            id: right
            width: 160
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Layout.fillHeight: true

            ColumnLayout {
                id: right_vbox
                
                spacing: 2
                
                Label {
                    id: log_label
                    text: qsTr("Data series:")
                }

                ListView {
                    id: series_list_view
                    width: 110
                    height: 160
                    Layout.fillWidth: true
                    model: dataModel
                    delegate: RowLayout {
                        CheckBox {
                            checked : selected
                            
                            onClicked: {
                                selected = checked;
                            }
                        }

                        Text {
                            text: name
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        spacing: 10
                    }
                }

                RowLayout {
                    id: rowLayout1
                    width: 100
                    height: 100

                    Label {
                        id: spin_label1
                        text: qsTr("X from")
                    }

                    SpinBox {
                        id: from_spin
                        value: draw_mpl.xFrom
                        minimumValue: 0
                        maximumValue: dataModel.lengthData - 1;
                        enabled: series_list_view.count > 0;
                    }
                    
                    Binding {
                        target: draw_mpl
                        property: "xFrom"
                        value: from_spin.value
                    }

                    Label {
                        id: spin_label2
                        text: qsTr("to")
                    }

                    SpinBox {
                        id: to_spin
                        value: draw_mpl.xTo
                        minimumValue: 0
                        maximumValue: dataModel.lengthData - 1;
                        enabled: series_list_view.count > 0;
                    }
                    
                    Binding {
                        target: draw_mpl
                        property: "xTo"
                        value: to_spin.value
                    }
                }

                CheckBox {
                    id: legend_cb
                    text: qsTr("Show Legend")
                    checked: draw_mpl.legend
                }
                
                Binding {
                    target: draw_mpl
                    property: "legend"
                    value: legend_cb.checked
                }
            }
        }
    }
}
