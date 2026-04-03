import * as THREE from 'three';
// import { RoundedBoxGeometry } from 'three/examples/jsm/Addons.js';

import type { World } from '@dimforge/rapier3d';

const sceneMiddle = new THREE.Vector3(0,0,0);
// const colorPallete = [0x780000, 0xc1121f, 0xfdf0d5, 0x003049, 0x669bbc];
// const colorPallete = [0x0067b1, 0x4e99ce, 0x9bcbeb, 0x55d7e2, 0xffffff, 0x9ca9b2, 0x4e6676, 0xf69230, 0xf5d81f];
// const colorPallete = [0xff6d00, 0xff7900, 0xff8500, 0xff9100, 0xff9e00, 0x240046, 0x3c096c, 0x5a189a, 0x7b2cbf, 0x9d4edd];

// geos:
// const geometries = [
//   new THREE.SphereGeometry(0.65, 32, 32),
//   new RoundedBoxGeometry(1.0, 1.0, 1.0, 2, 0.1),
//   // new THREE.IcosahedronGeometry(1.0, 0),
//   new THREE.TorusGeometry(0.65, 0.3, 16, 64),
//   new THREE.TorusKnotGeometry(0.65, 0.25, 128, 32),
//   new THREE.TetrahedronGeometry(1.0, 0),
//   // new THREE.OctahedronGeometry(1.0, 0),
//   // new THREE.DodecahedronGeometry(1.0),
// ];

///
// function getGeometry(size: number) {
//   const randomGeo = geometries[Math.floor(Math.random() * geometries.length)];
//   const geo = randomGeo.clone();
//   geo.scale(size, size, size);
//   return geo;
// }

///
function getBody(RAPIER: any, world: World) {

  //! ORI ---------------------------
  // const size = 0.5; // 0.1 + Math.random() * 0.25;
  // const range = 2;
  const size = 0.1 + Math.random() * 0.25;
  const range = 6;
  const density = size * 1.0;
  let x = Math.random() * range - range * 0.5;
  let y = Math.random() * range - range * 0.5 + 3;
  let z = Math.random() * range - range * 0.5;

  // let color = colorPallete[Math.floor(Math.random() * colorPallete.length)];
  // const geometry = getGeometry(size);
  // const prob = Math.random();
  // const options = prob < 0.33 ? {
  //   color,
  //   // flatShading: true,
  //   metalness: 1,
  //   roughness: 0.1
  // } : prob < 0.66 ? {
  //   roughness: 0.1,
  //   transmission: 1.0,
  //   transparent: true,
  //   thickness: 3.0,
  // } : {
  //   color,
  //   emissive: color,
  //   emissiveIntensity: 0.5,
  //   // wireframe: true,
  //   // flatShading: true,
  //   metalness: 0.0,
  //   roughness: 0.5,
  // };
  // const material = new THREE.MeshPhysicalMaterial(options);
  // const mesh = new THREE.Mesh(geometry, material);


  //! NEW ---------------------------
  // const geometry = geometries[0];
  const geometry = new THREE.IcosahedronGeometry(size, 1);

  const material = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });
  const mesh = new THREE.Mesh(geometry, material);
  // mesh.position.set(x, y, z);

  mesh.name = "ball";

  const wireMat = new THREE.MeshBasicMaterial({ color: 0x990000, wireframe: true });
  const wireMesh = new THREE.Mesh(geometry, wireMat);
  wireMesh.scale.setScalar(1.001);
  mesh.add(wireMesh);


  // physics
  let rigidBodyDesc = RAPIER.RigidBodyDesc.dynamic()
    .setTranslation(x, y, z)
    // .setLinearDamping(1)
    // .setAngularDamping(1);
  let rigid = world.createRigidBody(rigidBodyDesc);
  // let points = geometry.attributes.position.array;
  // let colliderDesc = RAPIER.ColliderDesc.convexHull(points).setDensity(density);
  let colliderDesc = RAPIER.ColliderDesc.ball(size).setDensity(density);
  world.createCollider(colliderDesc, rigid);


  function update() {
    rigid.resetForces(true);
    let { x, y, z } = rigid.translation();
    let pos = new THREE.Vector3(x, y, z);
    let dir = pos.clone().sub(sceneMiddle).normalize();
    // let q = rigid.rotation();
    // let rote = new THREE.Quaternion(q.x, q.y, q.z, q.w);
    // mesh.rotation.setFromQuaternion(rote);
    rigid.addForce(dir.multiplyScalar(-0.5), true);
    mesh.position.set(x, y, z);
  }

  return { mesh, rigid, update };
}

///
function getMouseBall(RAPIER: any, world: World) {
  const mouseSize = 0.25;
  const geo = new THREE.IcosahedronGeometry(mouseSize, 8);
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff });
  const mouseLight = new THREE.PointLight(0xffffff, 1);
  const mouseMesh = new THREE.Mesh(geo, mat);
  mouseMesh.add(mouseLight);
  // RIGID BODY
  let bodyDesc = RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(0, 0, 0);
  let mouseRigid = world.createRigidBody(bodyDesc);
  let dynamicCollider = RAPIER.ColliderDesc.ball(mouseSize * 3.0);
  world.createCollider(dynamicCollider, mouseRigid);

  function update(mouse: THREE.Vector2 ) {
    // mouseRigid.setTranslation({ x: mouse.x * 5, y: mouse.y * 5, z: mouse.z }, true);
    mouseRigid.setTranslation({ x: mouse.x * 5, y: mouse.y * 5, z: 0 }, true);
    let { x, y ,z } = mouseRigid.translation();
    // let { x, y, z} = { x: mouse.x * 5, y: mouse.y * 5, z: 1};
    mouseMesh.position.set(x, y, z);
  }

  return { mesh: mouseMesh, update };
}


export { getBody, getMouseBall };
