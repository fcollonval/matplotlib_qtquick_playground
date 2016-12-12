import QtQuick 2.6
import QtQuick.Layouts 1.2
import QtQuick.Controls 1.0
import QtQuick.Dialogs 1.2

Dialog {
    id: subplottool
    
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
                    minimumValue: bottom_slider.value
                    maximumValue: 1
                    value: 1
                    stepSize: 0.01
                    
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
                    minimumValue: 0
                    maximumValue: top_slider.value
                    value: 0
                    stepSize: 0.01
                    
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
                    minimumValue: 0
                    maximumValue: right_slider.value
                    value: 0
                    stepSize: 0.01
                    
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
                    minimumValue: left_slider.value
                    maximumValue: 1
                    value: 1
                    stepSize: 0.01
                    
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
                    minimumValue: 0
                    maximumValue: 1
                    value: 0
                    stepSize: 0.01
                    
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
                    minimumValue: 0
                    maximumValue: 1
                    value: 0
                    stepSize: 0.01
                    
                    Layout.fillWidth: true
                }
                Label{
                    text: wspace_slider.value.toFixed(2)
                }
            }
        }
        
        RowLayout {
            id: buttons
            
            Layout.alignment: Qt.AlignBottom | Qt.AlignHCenter
            Layout.fillWidth: true
            
            Button {
                id: tight_layout
                text: "Tight Layout"
                
                Layout.alignment: Qt.AlignLeft | Qt.Alignbottom
                
                onClicked: {
                    subplottool.tightLayout()
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
                    subplottool.reset()
                }
            }
            
            Button {
                id: close
                text: "Close"
                
                Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                
                onClicked: {
                    subplottool.close()
                }
            }
        }
    
    }
}