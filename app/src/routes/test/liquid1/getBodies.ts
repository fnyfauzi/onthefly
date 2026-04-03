import * as THREE from "three";

import type { World } from "@dimforge/rapier3d";

const sceneMiddle = new THREE.Vector3(0, 0, 0);
const metaOffset = new THREE.Vector3(0.5, 0.5, 0.5);
// const colorPallete = [0x780000, 0xc1121f, 0xfdf0d5, 0x003049, 0x669bbc];
const colorPallete = [0x0067b1, 0x4e99ce, 0x9bcbeb, 0x55d7e2, 0xffffff, 0x9ca9b2, 0x4e6676, 0xf69230, 0xf5d81f];

///
function getBody(RAPIER: any, world: World) {
  const size = 0.1 + Math.random() * 0.25; // 0.2
  // const size = 0.2;
  const range = 6;
  const density = size * 1.0; // 0.5
  // const density = 0.5;
  let x = Math.random() * range - range * 0.5;
  let y = Math.random() * range - range * 0.5 + 3;
  let z = Math.random() * range - range * 0.5;
  // physics
  let rigidBodyDesc = RAPIER.RigidBodyDesc.dynamic().setTranslation(x, y, z);
  let rigid = world.createRigidBody(rigidBodyDesc);
  let colliderDesc = RAPIER.ColliderDesc.ball(size).setDensity(density);
  world.createCollider(colliderDesc, rigid);
  //
  let color = colorPallete[Math.floor(Math.random() * colorPallete.length)];
  const geometry = new THREE.IcosahedronGeometry(size, 1);
  const material = new THREE.MeshPhysicalMaterial({
    color: color,
    flatShading: true,
    metalness: 1,
    roughness: 1,
  });
  const mesh = new THREE.Mesh(geometry, material);
  // mesh.position.set(x, y, z);

  function update() {
    rigid.resetForces(true);
    let { x, y, z } = rigid.translation();
    let pos = new THREE.Vector3(x, y, z);
    let dir = pos.clone().sub(sceneMiddle).normalize();
    rigid.addForce(dir.multiplyScalar(-0.5), true);
    pos.multiplyScalar(0.1).add(metaOffset);
    return pos;
  }

  return { mesh, rigid, update };
}

///
function getMouseBall(RAPIER: any, world: World) {
  const mouseSize = 0.25;
  const geo = new THREE.IcosahedronGeometry(mouseSize, 8);
  const mat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0xffffff,
  });
  // const mouseLight = new THREE.PointLight(0xffffff, 1);
  const mouseMesh = new THREE.Mesh(geo, mat);
  // mouseMesh.add(mouseLight);
  // RIGID BODY
  let bodyDesc = RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(0, 0, 0);
  let mouseRigid = world.createRigidBody(bodyDesc);
  let dynamicCollider = RAPIER.ColliderDesc.ball(mouseSize * 3.0);
  world.createCollider(dynamicCollider, mouseRigid);
  
  function update(mouse: THREE.Vector2) {
  // function update(mouse: THREE.Vector3) {
    mouseRigid.setTranslation({ x: mouse.x * 5, y: mouse.y * 5, z: 0 }, true);
    // mouseRigid.setTranslation({ x: mouse.x, y: mouse.y, z: mouse.z }, true); //! ORI
    // mouseRigid.setTranslation({ x: mouse.x * 5, y: mouse.y * 5, z: mouse.z * 5 }, true);
    let { x, y, z } = mouseRigid.translation();
    mouseMesh.position.set(x, y, z);
  }

  return { mesh: mouseMesh, update };
}

export { getBody, getMouseBall };
