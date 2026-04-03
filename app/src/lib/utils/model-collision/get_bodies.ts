import * as THREE from 'three';
import type { World } from '@dimforge/rapier3d';

const sceneMiddle = new THREE.Vector3(0,0,0);

///
function getBody(RAPIER: any, world: World) {
  const size = 0.1 + Math.random() * 0.25;
  const range = 6;
  const density = size * 1.0;
  let x = Math.random() * range - range * 0.5;
  let y = Math.random() * range - range * 0.5 + 3;
  let z = Math.random() * range - range * 0.5;

  const geometry = new THREE.IcosahedronGeometry(size, 1);
  const material = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = "ball";
  const wireMat = new THREE.MeshBasicMaterial({ color: 0x990000, wireframe: true });
  const wireMesh = new THREE.Mesh(geometry, wireMat);
  wireMesh.scale.setScalar(1.001);
  mesh.add(wireMesh);

  let rigidBodyDesc = RAPIER.RigidBodyDesc.dynamic().setTranslation(x, y, z)
  let rigid = world.createRigidBody(rigidBodyDesc);
  let colliderDesc = RAPIER.ColliderDesc.ball(size).setDensity(density);
  world.createCollider(colliderDesc, rigid);

  function update() {
    rigid.resetForces(true);
    let { x, y, z } = rigid.translation();
    let pos = new THREE.Vector3(x, y, z);
    let dir = pos.clone().sub(sceneMiddle).normalize();
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

  let bodyDesc = RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(0, 0, 0);
  let mouseRigid = world.createRigidBody(bodyDesc);
  let dynamicCollider = RAPIER.ColliderDesc.ball(mouseSize * 3.0);
  world.createCollider(dynamicCollider, mouseRigid);

  function update(mouse: THREE.Vector2 ) {
    mouseRigid.setTranslation({ x: mouse.x * 5, y: mouse.y * 5, z: 0 }, true);
    let { x, y ,z } = mouseRigid.translation();
    mouseMesh.position.set(x, y, z);
  }

  return { mesh: mouseMesh, update };
}

///
export { getBody, getMouseBall };
