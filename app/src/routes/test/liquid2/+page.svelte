<script lang="ts">
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import * as THREE from "three";
  import { ArcballControls, MarchingCubes } from "three/examples/jsm/Addons.js";
  import { getBody, getMouseBall } from "./getBodies";
  import type { RigidBody } from "@dimforge/rapier3d";
  import getBgSphere from "./getBgSphere";
  import { loadModel } from "$lib/utils/model_test_liquid";

  // Basic
  let container: Element | HTMLElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  // let directionalLight: THREE.DirectionalLight;
  let controls: ArcballControls;
  let clock: THREE.Clock;
  // let gui: GUI;

  let mouse: THREE.Vector2;
  //
  // let raycaster: THREE.Raycaster;
  // let pointer: THREE.Vector3;
  // let cameraDirection: THREE.Vector3;

  function init() {
    container = document.getElementById("demo")!;
    // scene
    scene = new THREE.Scene();
    // camera
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
    scene.add(camera);
    // renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    // renderer.shadowMap.enabled = true;
    // renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    // // directionalLight
    // directionalLight = new THREE.DirectionalLight("white", 10);
    // directionalLight.position.set(-0.8, 1.8, 2.7);
    // directionalLight.target.position.set(0, 0, 0);
    // // directionalLight.castShadow = true;
    // scene.add(directionalLight);
    // scene.add(new THREE.DirectionalLightHelper(directionalLight, 0.2));
    // controls
    controls = new ArcballControls(camera, renderer.domElement, scene);
    controls.update();
    // helpers
    scene.add(new THREE.GridHelper(3, 6)); // size, division
    // scene.add(new THREE.AxesHelper(2));
    const axesHelper = new THREE.AxesHelper(2);
    axesHelper.setColors("red", "green", "blue");
    axesHelper.position.set(-2, 0, -2);
    scene.add(axesHelper);
    // clock
    clock = new THREE.Clock();
    // gui
    // gui = new GUI();
    // gui.close();
    // mouse
    mouse = new THREE.Vector2();
    // pointer
    // raycaster = new THREE.Raycaster();
    // pointer = new THREE.Vector3();
    // cameraDirection = new THREE.Vector3();
  }

  if (browser) {
    onMount(async () => {
      init();
      camera.position.set(1, 2, 8);
      // camera.position.set(-3, 8, 2);

      //* Your code here...
      //

      /*
      If your scene appears too bright or washed out,
      consider applying tone mapping to your WebGLRenderer
      (e.g., renderer.toneMapping = THREE.ACESFilmicToneMapping;).
      */
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.8;

      // ------------------------------------
      // cubemap
      // const texture = await new THREE.TextureLoader().loadAsync(
      //   "/textures/gettyimages-1909960292-2048x2048.jpg"
      // );
      // texture.mapping = THREE.EquirectangularReflectionMapping;
      // texture.colorSpace = THREE.SRGBColorSpace;
      // scene.background = texture;
      // scene.environment = texture;

      // ------------------------------------
      const RAPIER = await import("@dimforge/rapier3d");
      // const gravity = { x: 0.0, y: -9.81, z: 0.0 };
      const gravity = { x: 0.0, y: 0.0, z: 0.0 };
      const world = new RAPIER.World(gravity);

      //
      type typeBody = {
        model: THREE.Object3D;
        rigid: RigidBody;
        update: () => THREE.Vector3;
      };
      const bodies: typeBody[] = [];
      const numBodies = 16;
      for (let i = 0; i < numBodies; i++) {
        // const body: typeBody = getBody(RAPIER, world);
        const body: typeBody = await loadModel(RAPIER, world, "sample.pdb");
        body.model.scale.set(0.5, 0.5, 0.5);
        bodies.push(body);
        // scene.add(body.mesh);
      }

      // ------------------------------------
      const mouseBall = getMouseBall(RAPIER, world);
      scene.add(mouseBall.mesh);

      // ------------------------------------
      // Metaballs
      const metaMat = new THREE.MeshPhysicalMaterial({
        vertexColors: true,
        transmission: 1.0,
        thickness: 1.0,
        roughness: 0.0,
        metalness: 0.0,
        transparent: true, // debug
        // opacity: 0.8,
      });
      const metaballs = new MarchingCubes(
        96, // resolution
        metaMat,
        true, // enableUVs
        true, // enableColors
        90000 // max poly count
      );
      metaballs.scale.setScalar(5);
      metaballs.isolation = 1000;
      metaballs.userData = {
        update() {
          metaballs.reset();
          const strength = 0.5; // size-y
          const subtract = 10; // lightness
          bodies.forEach((b) => {
            const { x, y, z } = b.update();
            const obj = b.model as THREE.Object3D;
            // obj.children.forEach((child, i) => {
            //   const mesh = child as THREE.Mesh;
            //   const mColor = (mesh.material as THREE.MeshPhysicalMaterial)
            //     .color;
            //   metaballs.addBall(x, y, z, strength, subtract, mColor);
            // });
            for (let i = 0; i < obj.children.length; i++) {
              const mesh = obj.children[i] as THREE.Mesh;
              const mColor = (mesh.material as THREE.MeshPhysicalMaterial)
                .color;
              metaballs.addBall(x, y, z, strength, subtract, mColor);
              break;
            }
          });
          metaballs.update();
        },
      };
      scene.add(metaballs);

      // ------------------------------------
      const hemiLight = new THREE.HemisphereLight(0x00bbff, 0xaa00ff);
      hemiLight.intensity = 0.2;
      scene.add(hemiLight);

      // ------------------------------------
      const bgSphere = getBgSphere({ hue: 0.565 });
      scene.add(bgSphere);

      // ------------------------------------
      //
      // renderer.setAnimationLoop(null);
      renderer.setAnimationLoop(() => {
        tick();
        renderer.render(scene, camera); // Replace with composer.render(delta);
        controls.update();
      });

      function tick() {
        // const delta = clock.getDelta();
        // cube.userData.update(delta);
        world.step();
        mouseBall.update(mouse);
        bodies.forEach((b: typeBody) => b.update());
        metaballs.userData.update();
      }
    });
  }
</script>

<svelte:window
  onresize={() => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
  }}
  onmousemove={(e: MouseEvent) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / window.innerWidth) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / window.innerHeight) * 2 + 1;
  }}
/>

<div id="demo" class="container-full">
  <!-- Reset button -->
  <button
    class="absolute left-2 top-2 btn btn-xs bg-white text-black"
    onclick={() => {
      setTimeout(() => {
        controls.reset();
        camera.position.set(1, 2, 8);
      }, 10);
    }}>Reset</button
  >
  <label for="" class="absolute left-10, top-6 text-4xl text-white"
    >Liquid Reaction</label
  >
</div>
