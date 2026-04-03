<script lang="ts">
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import * as THREE from "three";
  import { ArcballControls } from "three/examples/jsm/Addons.js";

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
    // axesHelper.setColors("red", "green", "blue");
    axesHelper.position.set(-2, 0, -2);
    scene.add(axesHelper);
    // clock
    clock = new THREE.Clock();
    // gui
    // gui = new GUI();
    // gui.close();
    // mouse
    mouse = new THREE.Vector2();
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

      //

      //
      // renderer.setAnimationLoop(null);
      renderer.setAnimationLoop(() => {
        tick();
        renderer.render(scene, camera);
        controls.update();
      });

      function tick() {
        // const delta = clock.getDelta();
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
    class="absolute left-2 top-2 btn btn-md bg-white text-black"
    onclick={() => {
      setTimeout(() => {
        controls.reset();
        camera.position.set(1, 2, 8);
      }, 10);
    }}>Reset</button
  >
  <label for="" class="absolute left-10, top-6 text-4xl text-white"
    >Meta Cube</label
  >
</div>
