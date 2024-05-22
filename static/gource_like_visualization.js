// This script will create an interactive Gource-like graph visualization using D3.js

// Define the dimensions and create the SVG container
const width = 960;
const height = 600;
const svg = d3.select('body').append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

// Placeholder data - to be replaced with data from Neo4j
let nodes = [
    // ...nodes data...
];
let links = [
    // ...links data...
];

// Create the simulation with forces
const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id))
    .force('charge', d3.forceManyBody())
    .force('center', d3.forceCenter(width / 2, height / 2));

// Create the link elements
const link = svg.append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(links)
    .enter().append('line')
    .attr('stroke-width', d => Math.sqrt(d.value));

// Create the node elements
const node = svg.append('g')
    .attr('class', 'nodes')
    .selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('r', 5)
    .attr('fill', d => color(d.group))
    .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

// Define the drag behaviors
function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Add tick event to update the positions
simulation.on('tick', () => {
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

    node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
});

// Add zoom behavior
svg.call(d3.zoom()
    .scaleExtent([1 / 2, 8])
    .on('zoom', zoomed));

function zoomed() {
    svg.attr('transform', d3.event.transform);
}

// Function to update the visualization with new data
function updateVisualization(newNodes, newLinks) {
    // Update the nodes and links with the new data
    // Restart the simulation

    // Clear the current nodes and links
    svg.selectAll('.nodes circle').remove();
    svg.selectAll('.links line').remove();

    // Update the nodes and links with the new data
    nodes.splice(0, nodes.length, ...newNodes);
    links.splice(0, links.length, ...newLinks);

    // Restart the simulation with the new data
    simulation.nodes(nodes);
    simulation.force('link').links(links);
    simulation.alpha(1).restart();
}

// This is a placeholder function to demonstrate how the visualization would be updated
// It will need to be connected to the Streamlit application to receive real-time data updates

// Function to color the nodes
function color(group) {
    const scale = d3.scaleOrdinal(d3.schemeCategory10);
    return scale(group);
}

// Function to start the drag behavior
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

// Function to drag the nodes
function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

// Function to end the drag behavior
function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Function to handle the zoom behavior
function zoomed(event) {
    svg.attr('transform', event.transform);
}

// Function to update the visualization with new data
function updateVisualization(newNodes, newLinks) {
    // Clear the current nodes and links
    svg.selectAll('.nodes circle').remove();
    svg.selectAll('.links line').remove();

    // Update the nodes and links with the new data
    nodes = newNodes;
    links = newLinks;

    // Restart the simulation with the new data
    simulation.nodes(nodes).on('tick', ticked);
    simulation.force('link').links(links);
    simulation.alpha(1).restart();

    // Create the link elements
    link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('stroke-width', d => Math.sqrt(d.value));

    // Create the node elements
    node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('r', 5)
        .attr('fill', d => color(d.group))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
}

// Function to update positions each tick
function ticked() {
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

    node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
}
