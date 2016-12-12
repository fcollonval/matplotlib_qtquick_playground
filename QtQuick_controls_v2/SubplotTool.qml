import QtQuick 2.6
import QtQuick.Layouts 1.2
import Qt.labs.controls 1.0
import QtQuick.Dialogs 1.2

Dialog {
    id: subplotTool
    
    title: "Margins & spacing"
    
    property alias left: left_slider
    property alias right: right_slider
    property alias top: top_slider
    property alias bottom: bottom_slider
    property alias hspace: hspace_slider
    property alias wspace: wspace_slider
    
    signal reset
    signal tightLayout
        
    contentItem : ColumnLayout {
        anchors.fill: parent
        
        GroupBox {
            id: borders
            title: "Borders"
            
            Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            GridLayout{
                columns: 3
                anchors.fill: parent
                
                Label {
                    text: "top"
                }
                Slider{
                    id: top_slider
                    from: bottom_slider.value
                    to: 1
                    value: 1
                    stepSize: 0.01
                    snapMode: Slider.SnapOnRelease
                    
                    Layout.fillWidth: true
                }
                Label{
                    text: top_slider.value.toFixed(2)
                }
                
                Label {
                    text: "bottom"
                }
                Slider{
                    id: bottom_slider
                    from: 0
                    to: top_slider.value
                    value: 0
                    stepSize: 0.01
                    snapMode: Slider.SnapOnRelease
                    
                    Layout.fillWidth: true
                }
                Label{
                    text: bottom_slider.value.toFixed(2)
                }
                
                Label {
                    text: "left"
                }
                Slider{
                    id: left_slider
                    from: 0
                    to: right_slider.value
                    value: 0
                    stepSize: 0.01
                    snapMode: Slider.SnapOnRelease
                    
                    Layout.fillWidth: true
                }
                Label{
                    text: left_slider.value.toFixed(2)
                }
                
                Label {
                    text: "right"
                }
                Slider{
                    id: right_slider
                    from: left_slider.value
                    to: 1
                    value: 1
                    stepSize: 0.01
                    snapMode: Slider.SnapOnRelease
                    
                    Layout.fillWidth: true
                }
                Label{
                    text: right_slider.value.toFixed(2)
                }
                    
            }
        }
        
        GroupBox {
            id: spacings
            title: "Spacings"
            
            Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            GridLayout{
                columns: 3
                anchors.fill: parent
            
                Label {
                    text: "hspace"
                }
                Slider{
                    id: hspace_slider
                    from: 0
                    to: 1
                    value: 0
                    stepSize: 0.01
                    snapMode: Slider.SnapOnRelease
                    
                    Layout.fillWidth: true
                }
                Label{
                    text: hspace_slider.value.toFixed(2)
                }
                
                Label {
                    text: "wspace"
                }
                Slider{
                    id: wspace_slider
                    from: 0
                    to: 1
                    value: 0
                    stepSize: 0.01
                    snapMode: Slider.SnapOnRelease
                    
                    Layout.fillWidth: true
                }
                Label{
                    text: wspace_slider.value.toFixed(2)
                }
            }
        }
        
        RowLayout {
            id: buttons
            
            anchors.bottom: parent.bottom
            Layout.fillWidth: true
            
            Button {
                id: tight_layout
                text: "Tight Layout"
                
                Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
                
                onClicked: {
                    subplotTool.tightLayout()
                }
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            Button {
                id: reset
                text: "Reset"
                
                Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                
                onClicked: {
                    subplotTool.reset()
                }
            }
            
            Button {
                id: close
                text: "Close"
                
                Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                
                onClicked: {
                    subplotTool.close()
                }
            }
        }
    
    }
}