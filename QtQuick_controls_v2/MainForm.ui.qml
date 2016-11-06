import QtQuick 2.6
import Qt.labs.controls 1.0
import QtQuick.Layouts 1.3

Item {
    anchors.fill: parent

    RowLayout {
        id: hbox
        spacing: 5
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.fill: parent
        
        Image {
            id: canvas_mpl
//            width: 480
//            height: 320
//            Layout.fillHeight: true
//            Layout.fillWidth: true
            fillMode: Image.PreserveAspectCrop
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
            onStatusTextChanged: {
                root.footer.text = draw_mpl.statusText;
            }
        }
        
        Connections {
            target: dataModel
            onDataChanged: {
                draw_mpl.update_figure()
            }
        }

        Pane {
            id: right
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Layout.fillHeight: true
            Layout.fillWidth: true

            ColumnLayout {
                id: right_vbox
                
                spacing: 2
                
                Label {
                    id: log_label
                    text: qsTr("Data series:")
                }

                ListView {
                    id: series_list_view
                    height: 180
                    Layout.fillWidth: true
                    
                    clip: true
                    
                    model: dataModel
                    delegate: CheckBox {
                        checked : false;
                        text: name
                        onClicked: {
                            selected = checked;
                        }
                    }
                }

                RowLayout {
                    id: rowLayout1
                    Layout.fillWidth: true

                    Label {
                        id: spin_label1
                        text: qsTr("X")
                    }

                    RangeSlider {
                        id: xSlider
                        first.value: draw_mpl.xFrom
                        second.value: draw_mpl.xTo
                        from: 0
                        to: dataModel.lengthData - 1;
                        enabled: series_list_view.count > 0;
                        
                    }
                    
                    Binding {
                        target: draw_mpl
                        property: "xFrom"
                        value: xSlider.first.value
                    }
                    
                    Binding {
                        target: draw_mpl
                        property: "xTo"
                        value: xSlider.second.value
                    }
                    
                }

                Switch {
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
