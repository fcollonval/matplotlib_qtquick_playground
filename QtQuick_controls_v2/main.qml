import QtQuick 2.6
import Qt.labs.controls 1.0
import QtQuick.Dialogs 1.2
import QtQuick.Layouts 1.0
import QtQuick.Window 2.1
import Qt.labs.controls.material 1.0
import Qt.labs.controls.universal 1.0

ApplicationWindow {
    id: root
    visible: true
    width: 940
    height: 500
    title: qsTr("Hello World")
    
    Material.theme : Material.Light
    Material.accent : Material.LightGreen
    Universal.theme : Universal.Light
    Universal.accent : Universal.Amber

    FileDialog {
        id: fileDialog
        nameFilters: ["CSV files (*.csv)", "All Files (*.*)"]
        onAccepted: {
            draw_mpl.filename = fileUrl
        }
    } 

    header: ToolBar {
        id: head
        
        RowLayout {
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            anchors.fill: parent
            ToolButton {
                width: 32
//                text: qsTr("Load a file")
                contentItem: Image{
                    fillMode: Image.PreserveAspectFit
                    source: "document-open.svg"
                }
                onClicked: {
                    fileDialog.open()
                }
            }
            ToolButton{
                width: 32
//                text: qsTr("About")
                contentItem: Image{
                    fillMode: Image.PreserveAspectFit
                    source: "help-about.svg"
                }
                onClicked: messageDialog.show("About the demo", draw_mpl.about)
            }
            ToolButton {
                width: 32
//                text: qsTr("Quit")
                contentItem: Image{
                    fillMode: Image.PreserveAspectFit
                    source: "window-close.svg"
                }
                onClicked: Qt.quit();
            }            
            Item {
                Layout.fillWidth: true
            }
        }
    }    

    MainForm {
        id: mainView
        width: parent.width
        height: 320
        
        transform: [
            Scale {
                id: scale; 
                xScale: yScale;
                yScale: Math.min(root.width/mainView.width,
                                 (root.height-head.height-foot.height)/mainView.height);
            },
            Translate {
                x: (root.width-mainView.width*scale.xScale)/2;
                y: (root.height-head.height-foot.height-mainView.height*scale.yScale)/2;}
            ]
    }
    
    footer: Label {
        id: foot
        text: draw_mpl.statusText
    }

    MessageDialog {
        id: messageDialog

        function show(title, caption) {
            messageDialog.title = title;
            messageDialog.text = caption;
            messageDialog.open();
        }
    }
}
