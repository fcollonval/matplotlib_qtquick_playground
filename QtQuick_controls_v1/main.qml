import QtQuick 2.6
import QtQuick.Controls 1.5
import QtQuick.Dialogs 1.2
import QtQuick.Layouts 1.0
import QtQuick.Window 2.1

ApplicationWindow {
    visible: true
    width: 640
    height: 335
    title: qsTr("Hello World")

    FileDialog {
        id: fileDialog
        nameFilters: ["CSV files (*.csv)", "All Files (*.*)"]
        onAccepted: {
            draw_mpl.filename = fileUrl
        }
    }    
    
    menuBar: MenuBar {
        Menu {
            title: qsTr("&File")
            MenuItem {
                text: qsTr("&Load a file")
                onTriggered: {
                    fileDialog.open()
                }
            }
            MenuItem {
                text: qsTr("&Quit")
                onTriggered: Qt.quit();
            }
        }
        Menu {
            title: qsTr("&Help")

            MenuItem{
                text: qsTr("&About")
                onTriggered: messageDialog.show("About the demo", draw_mpl.about)
            }
        }
    }

    MainForm {
        anchors.fill: parent
    }
    
    statusBar: Text {
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
