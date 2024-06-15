'use strict';

// See https://interactjs.io/

window.shark = window.shark || {};

const MIN_DIM = 50;

function makeSelectionBox(containerQuery) {
    let container = document.querySelector(containerQuery);

    let selection = document.createElement('div');
    selection.classList.add('selection');

    container.appendChild(selection);

    let selectionQuery = `${containerQuery} .selection`;

    interact(selectionQuery)
        .resizable({
            // Resize from all edges and corners.
            edges: {
                left: true,
                right: true,
                bottom: true,
                top: true,
            },
            listeners: {
                move: window.shark.dragResizeListener
            },
            modifiers: [
                // Keep the edges inside the parent.
                interact.modifiers.restrictEdges({
                    outer: 'parent'
                }),

                // Minimum Size
                interact.modifiers.restrictSize({
                    min: {
                        width: MIN_DIM,
                        height: MIN_DIM,
                    }
                })
            ],
        })
        .draggable({
            listeners: {
                move: window.shark.dragMoveListener
            },
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'parent',
                    endOnly: true
                })
            ]
        });
}

function dragResizeListener(event) {
    let target = event.target;

    let x = (parseFloat(target.getAttribute('data-x')) || 0);
    let y = (parseFloat(target.getAttribute('data-y')) || 0);

    // Update the element's style.
    target.style.width = event.rect.width + 'px';
    target.style.height = event.rect.height + 'px';

    // Translate when resizing from top or left edges.
    x += event.deltaRect.left;
    y += event.deltaRect.top;

    target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
}

function dragMoveListener(event) {
    let target = event.target;

    // Keep the dragged position in the data-x/data-y attributes.
    let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
    let y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

    // Translate the element.
    target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';

    // Update the posiion attributes;
    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
}

// Stach global functions.
window.shark.dragMoveListener = dragMoveListener;
window.shark.dragResizeListener = dragResizeListener;
