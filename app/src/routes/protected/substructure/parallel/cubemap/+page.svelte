<script lang="ts">
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import * as THREE from "three";

  import { ArcballControls, CSS2DRenderer } from "three/examples/jsm/Addons.js";
  import GUI from "lil-gui";

  import { EXRLoader } from "three/examples/jsm/Addons.js";
  import { loadModel } from "$lib/utils/model_cubemap";

  let { data } = $props();

  let model: THREE.Mesh;
  let hidden: boolean = $state(false);
  let currTexture: THREE.DataTexture | THREE.CubeTexture | THREE.Texture;
  let isAnimate = $state(false);

  let isHideH: boolean = $state(false); // Atom Hidrogen (toggle)

  let isSound: boolean = true;
  let volume: number = 0.2; // 0.5 = half

  // Realistic means:
  // TRUE  = Reality: set "scene.environment = texture" , and no texturing geometry material in object
  // FALSE = Fake   : not-set "scene.environment" , texturing geometry material
  const isRealistic: boolean = true;

  // Basic
  let container: Element | HTMLElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  // let labelRenderer: CSS2DRenderer;
  let controls: ArcballControls;
  let clock: THREE.Clock;
  let gui: GUI;

  // let mouse: THREE.Vector2;

  // Sound
  let audioLoader: THREE.AudioLoader;
  let audioListener: THREE.AudioListener;
  let audio: THREE.Audio;

  function init() {
    container = document.getElementById("demo")!;
    // scene
    scene = new THREE.Scene();
    // camera
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
    scene.add(camera);
    // renderer
    // renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(container.clientWidth, container.clientHeight, false);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    // renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    // label renderer
    // labelRenderer = new CSS2DRenderer();
    // labelRenderer.setSize(container.clientWidth, container.clientHeight);
    // labelRenderer.domElement.style.position = "absolute";
    // labelRenderer.domElement.style.top = "0px";
    // labelRenderer.domElement.style.pointerEvents = "none";
    // container.appendChild(labelRenderer.domElement);
    // controls
    controls = new ArcballControls(camera, renderer.domElement, scene);
    controls.update();
    // clock
    clock = new THREE.Clock();
    // gui
    gui = new GUI();
    // gui.close();
    // audio
    audioLoader = new THREE.AudioLoader();
    audioListener = new THREE.AudioListener();
    audio = new THREE.Audio(audioListener);
  }

  if (browser) {
    onMount(async () => {
      init();
      camera.position.set(1, 1, 5);

      //* Your code here...
      //

      /*
      If your scene appears too bright or washed out,
      consider applying tone mapping to your WebGLRenderer
      (e.g., renderer.toneMapping = THREE.ACESFilmicToneMapping;).
      */
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.8;

      // --------------------------
      // Street (EXR)
      // const street = await new EXRLoader().loadAsync("/textures/wide_street_01_2k.exr");
      // street.mapping = THREE.EquirectangularReflectionMapping;
      // street.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // drachenfels (Cubemap)
      // const drachenfels = new THREE.CubeTextureLoader().load([
      //   "/textures/drachenfels/posx.png",
      //   "/textures/drachenfels/negx.png",
      //   "/textures/drachenfels/posy.png",
      //   "/textures/drachenfels/negy.png",
      //   "/textures/drachenfels/posz.png",
      //   "/textures/drachenfels/negz.png",
      // ]);
      // drachenfels.mapping = THREE.CubeReflectionMapping;
      // drachenfels.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Equi
      // const equi = await new THREE.TextureLoader().loadAsync("/textures/equi.jpeg");
      // equi.mapping = THREE.EquirectangularReflectionMapping;
      // equi.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Home
      // const home = await new THREE.TextureLoader().loadAsync("/textures/2294472375_24a3b8ef46_o.jpg");
      // home.mapping = THREE.EquirectangularReflectionMapping;
      // home.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Space
      // const space = await new THREE.TextureLoader().loadAsync("/textures/space.jpeg");
      // space.mapping = THREE.EquirectangularReflectionMapping;
      // space.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Mol 1
      const mol1 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-173596847-2048x2048.jpg"
      );
      mol1.mapping = THREE.EquirectangularReflectionMapping;
      mol1.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Mol 2
      const mol2 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-182807377-2048x2048.jpg"
      );
      mol2.mapping = THREE.EquirectangularReflectionMapping;
      mol2.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Mol 3
      const mol3 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-1429885885-2048x2048.jpg"
      );
      mol3.mapping = THREE.EquirectangularReflectionMapping;
      mol3.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Mol 4
      const mol4 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-2172900622-2048x2048.jpg"
      );
      mol4.mapping = THREE.EquirectangularReflectionMapping;
      mol4.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Mol 5
      const mol5 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-1836050840-2048x2048.jpg"
      );
      mol5.mapping = THREE.EquirectangularReflectionMapping;
      mol5.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Mol 6
      const mol6 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-2225232174-2048x2048.jpg"
      );
      mol6.mapping = THREE.EquirectangularReflectionMapping;
      mol6.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      // Mol 7
      const mol7 = await new THREE.TextureLoader().loadAsync(
        "/textures/gettyimages-1909960292-2048x2048.jpg"
      );
      mol7.mapping = THREE.EquirectangularReflectionMapping;
      mol7.colorSpace = THREE.SRGBColorSpace;

      // --------------------------
      const createModel = async function (
        texture: THREE.DataTexture | THREE.CubeTexture | THREE.Texture,
        envMapType:
          | typeof THREE.EquirectangularReflectionMapping
          | typeof THREE.CubeReflectionMapping
      ) {
        model = (await loadModel(
          // data.name,
          // "sample.pdb",
          // "parallel/similarity",
          `/substructure/parallel/${data.subDir}/pdbs`,
          data.file,
          texture,
          envMapType,
          isRealistic
          // document,
          // container
        )) as THREE.Mesh;
        model.name = "model";
        if (isHideH) {
          model.children.forEach((child, i) => {
            if (child.name === "H" || child.name === "H-bound") {
              (child as THREE.Mesh).visible = isHideH ? false : true;
              // modelSelected!.remove(child);
            }
          });
        }
        scene.add(model);
        model.scale.set(0.5, 0.5, 0.5);
      };
      await createModel(mol1, THREE.EquirectangularReflectionMapping); // Initial, default
      scene.background = mol1; // Initial, default
      if (isRealistic) scene.environment = mol1;
      currTexture = mol1;

      // --------------------------
      const removeModel = function () {
        scene.children.forEach((e) => {
          if (e.name === "model") {
            scene.remove(e);
          }
        });
      };

      // --------------------------
      // const updateMaterialModel = function (
      //   model: THREE.Mesh,
      //   texture: THREE.DataTexture | THREE.CubeTexture | THREE.Texture
      // ) {
      //   (model.material as THREE.MeshStandardMaterial).envMap = texture;
      //   (model.material as THREE.MeshStandardMaterial).needsUpdate = true;
      //   // model.userData.update();
      // };

      // --------------------------
      // GUI
      const props = { texture: "mol1" };

      // --------------------------
      gui
        .add(props, "texture", [
          "mol1",
          "mol2",
          "mol3",
          "mol4",
          "mol5",
          "mol6",
          "mol7",
        ])
        .onChange((value: string) => {
          switch (value) {
            case "mol1":
              currTexture = mol1;
              if (!hidden) scene.background = mol1;
              if (isRealistic) scene.environment = mol1;
              // updateMaterialModel(model, mol1);
              removeModel();
              createModel(mol1, THREE.EquirectangularReflectionMapping);
              // isHideH = false;
              // isHidePolar = false;
              break;
            case "mol2":
              currTexture = mol2;
              if (!hidden) scene.background = mol2;
              if (isRealistic) scene.environment = mol2;
              // updateMaterialModel(model, mol2);
              removeModel();
              createModel(mol2, THREE.EquirectangularReflectionMapping);
              // isHideH = false;
              // isHidePolar = false;
              break;
            case "mol3":
              currTexture = mol3;
              if (!hidden) scene.background = mol3;
              if (isRealistic) scene.environment = mol3;
              // updateMaterialModel(model, mol3);
              removeModel();
              createModel(mol3, THREE.CubeReflectionMapping);
              // isHideH = false;
              // isHidePolar = false;
              break;
            case "mol4":
              currTexture = mol4;
              if (!hidden) scene.background = mol4;
              if (isRealistic) scene.environment = mol4;
              // scene.environment = mol4;
              // updateMaterialModel(model, mol4);
              removeModel();
              createModel(mol4, THREE.EquirectangularReflectionMapping);
              // isHideH = false;
              // isHidePolar = false;
              break;
            case "mol5":
              currTexture = mol5;
              if (!hidden) scene.background = mol5;
              if (isRealistic) scene.environment = mol5;
              // updateMaterialModel(model, mol5);
              removeModel();
              createModel(mol5, THREE.EquirectangularReflectionMapping);
              // isHideH = false;
              // isHidePolar = false;
              break;
            case "mol6":
              currTexture = mol6;
              if (!hidden) scene.background = mol6;
              if (isRealistic) scene.environment = mol6;
              // updateMaterialModel(model, mol6);
              removeModel();
              createModel(mol6, THREE.EquirectangularReflectionMapping);
              // isHideH = false;
              // isHidePolar = false;
              break;
            case "mol7":
              currTexture = mol7;
              if (!hidden) scene.background = mol7;
              if (isRealistic) scene.environment = mol7;
              // updateMaterialModel(model, mol7);
              removeModel();
              createModel(mol7, THREE.EquirectangularReflectionMapping);
              // isHideH = false;
              // isHidePolar = false;
              break;
            default:
              break;
          }
        });

      // ------------------------------------
      // Audio
      if (isSound) {
        audioLoader.load("/audio/space-chords-405055.mp3", (buffer) => {
          audio.setBuffer(buffer);
          audio.setLoop(true);
          audio.setVolume(volume);
          // audio.play();
        });
      }

      // ------------------------------------
      let delta = 0;
      let interval = 1 / 30;
      // renderer.setAnimationLoop(null);
      renderer.setAnimationLoop((time: number) => {
        delta += clock.getDelta();
        if (delta > interval) {
          tick(time);
          renderer.render(scene, camera);
          // labelRenderer.render(scene, camera);
          controls.update();
          delta = delta % interval;
        }
      });

      function tick(time: number) {
        // const delta = clock.getDelta();
        // cube.userData.update(delta);
        // model.userData.update();
        if (isAnimate) {
          model.rotation.x = time / 1000;
          model.rotation.y = time / 1000;
        }
      }
    });
  }
</script>

<svelte:window
  onresize={() => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    // labelRenderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
  }}
  onmousemove={(e: MouseEvent) => {
    // const rect = renderer.domElement.getBoundingClientRect();
    // mouse.x = ((e.clientX - rect.left) / window.innerWidth) * 2 - 1;
    // mouse.y = -((e.clientY - rect.top) / window.innerHeight) * 2 + 1;
  }}
/>

<div id="demo" class="container-full">
  <!-- Reset button -->
  <button
    class="absolute w-full/2 top-2 btn btn-lg bg-white text-black"
    onclick={() => {
      setTimeout(() => {
        controls.reset();
        camera.position.set(1, 1, 5);
      }, 10);
    }}>Reset</button
  >
  <!-- Show/Hide Scene button -->
  <button
    class="absolute left-[1.2rem] top-2 btn btn-lg bg-white text-black"
    onclick={() => {
      if (hidden) {
        hidden = !hidden;
        scene.background = currTexture;
      } else {
        hidden = !hidden;
        scene.background = new THREE.Color(0);
      }
    }}>{hidden ? "Show" : "Hide"} Scene</button
  >
  <!-- Start/Stop Animate button -->
  <button
    class="absolute left-50 top-2 btn btn-lg bg-white text-black"
    onclick={() => {
      isAnimate = !isAnimate;
      if (isSound) {
        if (isAnimate) {
          audio.play();
        } else {
          // audio.stop();
          audio.pause();
        }
      }
    }}>{isAnimate ? "Stop" : "Start"} Animate</button
  >
  <!-- Text (molecule's symbols) -->
  <div
    class="absolute w-52 left-8 top-[calc(12%)] text-lg text-white rounded-r-box border-r-2 border-b-2 border-b-red-400 pr-1 pb-2"
  >
    <div class="flex items-center space-x-1">
      <span class="font-semibold">H</span>
      <span>white</span>
      <span class="font-semibold ml-2">
        <div class="flex flex-col space-y-2">
          <button
            class="btn btn-xs bg-white text-black"
            onclick={() => {
              isHideH = !isHideH;
              model.children.forEach((child, i) => {
                if (child.name === "H" || child.name === "H-bound") {
                  (child as THREE.Mesh).visible = isHideH ? false : true;
                  // model.remove(child);
                }
              });
              scene.children.forEach((e) => {
                if (e.name === "model") {
                  scene.remove(e);
                }
              });
              scene.add(model);
            }}
          >
            {isHideH ? "Show Hydrogen" : "Hide Hydrogen"}
          </button>
        </div>
      </span>
    </div>
    <p><span class="text-gray-500 font-semibold">C</span> grey</p>
    <p><span class="font-semibold text-blue-500">N</span> blue</p>
    <p><span class="font-semibold text-red-500">O</span> red</p>
    <p><span class="font-semibold text-purple-500">P</span> purple</p>
    <p><span class="font-semibold text-yellow-300">S</span> yellow</p>
    <p><span class="font-semibold text-green-500">F</span> green</p>
    <p><span class="font-semibold text-lime-500">Cl</span> limegreen</p>
    <p><span class="font-semibold text-pink-500">Br</span> pink</p>
    <p><span class="font-semibold text-[#e400f5]">I</span> magentas</p>
    <p><span class="font-semibold text-orange-500">Si</span> orange</p>
  </div>
</div>
