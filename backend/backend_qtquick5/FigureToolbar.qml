import Backend 1.0
import QtQuick 2.6
import QtQuick.Layouts 1.2
import Qt.labs.controls 1.0
import QtQuick.Dialogs 1.2

Item{           
    width: 480
    height: 320 + 32

    ColumnLayout {
        spacing : 0
        anchors.fill: parent
        

        FigureCanvas {
            id: mplView
            objectName : "figure"
                        
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            Layout.minimumWidth: 10
            Layout.minimumHeight: 10
        }
        
        MessageDialog {
            id: messageDialog
        }
        
        FileDialog {
            id: saveFileDialog
            title: "Choose a filename to save to"
            folder: mplView.defaultDirectory
            nameFilters: mplView.fileFilters
            selectedNameFilter: mplView.defaultFileFilter
            selectExisting: false
            
            onAccepted: {
                try{
                    mplView.print_figure(fileUrl)
                }
                catch (error){
                    messageDialog.title = "Error saving file"
                    messageDialog.text = error
                    messageDialog.icon = StandardIcon.Critical
                    messageDialog.open()
                }
            }
        } 

        ToolBar {
            id: toolbar
            
            Layout.alignment: Qt.AlignLeft | Qt.Bottom
        
            RowLayout {
                Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                anchors.fill: parent
                spacing: 0
                
                ToolButton {
                    id : home
                    width: height
                    contentItem: Image{
                        fillMode: Image.PreserveAspectFit
                        source: "image://mplIcons/home"
                    }
                    onClicked: {
                    }
                }     
                
                ToolButton {
                    id : back
                    width: height
                    contentItem: Image{
                        fillMode: Image.PreserveAspectFit
                        source: "image://mplIcons/back"
                    }
                    onClicked: {
                    }
                }     
                
                ToolButton {
                    id : forward
                    width: height
                    
                    contentItem: Image{
                        fillMode: Image.PreserveAspectFit
                        source: "image://mplIcons/forward"
                    }
                    onClicked: {
                    }
                }     

                // Fake separator
                Label {
                    text : "|"
                }
                
                ToolButton {
                    id : pan
                    width: height
                    
                    contentItem: Image{
                        fillMode: Image.PreserveAspectFit
                        source: "image://mplIcons/move"
                    }
                    
                    checkable: true
                    
                    onClicked: {
//                        mplView.pan()
                    }
                }     
                
                ToolButton {
                    id : zoom
                    width: height
                    
                    contentItem: Image{
                        fillMode: Image.PreserveAspectFit
                        source: "image://mplIcons/zoom_to_rect"
                    }
                    
                    checkable: true
                    
                    onClicked: {
                    }
                }   

                Label {
                    text : "|"
                }
                
                ToolButton {
                    id : subplots
                    width: height
                    contentItem: Image{
                        fillMode: Image.PreserveAspectFit
                        source: "image://mplIcons/subplots"
                    }
                    onClicked: {
                    }
                }
                
                ToolButton {
                    id : save
                    width: height
                    contentItem: Image{
                        fillMode: Image.PreserveAspectFit
                        source: "image://mplIcons/filesave"
                    }
                    onClicked: {
                        saveFileDialog.open()
                    }
                }      
                
                Item {
                    Layout.fillWidth: true
                }
                
                Label{
                    id: locLabel
                    
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    
                    text: mplView.message
                }
            }
        }
    }
}    