## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4541 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4559 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4596 | 1.00 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4591 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4587 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.454) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_offset:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_adjust:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_offset: status=consumed; consumers=target.offset.z (replace)
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_adjust: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.454
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1327 |
| descend_grasp | 1.00 | 0.1261 |
| grasp_object | 1.00 | 0.0124 |
| lift_object | 1.00 | 0.1528 |
| transport_to_goal | 1.00 | 0.1941 |
| descend_to_place | 1.00 | 0.0692 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.000, 0.171) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.495, 0.000, 0.171)→(0.493, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.493, 0.001, 0.045)→(0.485, 0.000, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.485, 0.000, 0.036)→(0.493, 0.000, 0.189) | (0.497, 0.001, 0.026)→(0.512, 0.001, 0.175) | 0.266→0.204 |
| transport_to_goal | approach | 1.00 / step_budget | (0.493, 0.000, 0.189)→(0.569, 0.157, 0.264) | (0.512, 0.001, 0.175)→(0.583, 0.156, 0.245) | 0.204→0.066 |
| descend_to_place | descend | 1.00 / step_budget | (0.569, 0.157, 0.264)→(0.576, 0.176, 0.198) | (0.583, 0.156, 0.245)→(0.586, 0.176, 0.175) | 0.066→0.015 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.234
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.468
- phase_breakdown.lift_object_score: 0.221
- phase_breakdown.place_goal_score: 0.713
- phase_breakdown.reach_grasp_score: 0.228
- grasp_place_fitness: 0.975

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.975
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.454
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.383


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53431,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1066,"approach_object.generator.speed":0.13324,"descend_grasp.grasp_z":1e-05,"descend_to_place.descend_speed":0.0725,"descend_to_place.place_z_adjust":-0.0067,"grasp_object.grasp_offset":-0.0181,"lift_object.lift_height":0.21948,"transport_to_goal.transport_speed":0.05436},"optimized_scores":{"best_composite_score":0.45402,"best_fitness_score":0.97402,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.51126,-0.02177,-0.00156],"force_p95":0.49433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51616,"mean_force":0.18527,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49896,-0.02186,0.03638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3588.0,"contact_point_centroid":[0.50503,-0.00285,0.11047],"force_p95":0.11719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3095,"mean_force":0.07748,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50231,-0.02183,0.10796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3991.0,"contact_point_centroid":[0.50489,-0.04068,0.10749],"force_p95":0.1147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29262,"mean_force":0.07204,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50216,-0.02183,0.10573]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1201.0,"contact_point_centroid":[0.55304,0.15107,0.2621],"force_p95":0.19904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28256,"mean_force":0.11185,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54733,0.13295,0.26421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1331.0,"contact_point_centroid":[0.55277,0.11447,0.26325],"force_p95":0.18552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26087,"mean_force":0.10574,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54727,0.13257,0.26562]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51373,-0.02282,-0.0021],"force_p95":0.15243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21788,"mean_force":0.13054,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50144,-0.02192,0.03654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2518.0,"contact_point_centroid":[0.53297,0.06972,0.25227],"force_p95":0.1312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19841,"mean_force":0.09764,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52702,0.05109,0.25022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3060.0,"contact_point_centroid":[0.53177,0.02806,0.24821],"force_p95":0.11811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19424,"mean_force":0.08803,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52583,0.04644,0.24729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.50091,-0.00268,0.03805],"force_p95":0.07957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14116,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50028,-0.02189,0.03529]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.5137,-0.02302,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50396,-0.0086,0.23481]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50766,-0.02005,0.10488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.50093,-0.04101,0.03712],"force_p95":0.07183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08141,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50028,-0.02189,0.0353]}],"total_contact_groups":12},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55501,0.14201,0.20817],"final_tcp_position":[0.54934,0.14271,0.23212],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.50852,-0.0181,0.16518],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13935,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50887,-0.02206,0.04494],"tcp_start":[0.50852,-0.0181,0.16518],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02197,0.02565],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26521,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50025,-0.02189,0.03526],"tcp_start":[0.50887,-0.02206,0.04494],"tcp_to_object_dist_end":0.01646,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.53005,-0.02189,0.19255],"object_pos_start":[0.51361,-0.02197,0.02565],"object_to_goal_dist_end":0.17766,"object_to_goal_dist_start":0.26521,"object_z_max":0.1919,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50925,-0.02187,0.20602],"tcp_start":[0.50025,-0.02189,0.03526],"tcp_to_object_dist_end":0.02478,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5608,0.12271,0.27626],"object_pos_start":[0.53005,-0.02189,0.19255],"object_to_goal_dist_end":0.06187,"object_to_goal_dist_start":0.17766,"object_z_max":0.27593,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.5457,0.12277,0.29625],"tcp_start":[0.50925,-0.02187,0.20602],"tcp_to_object_dist_end":0.02505,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.55501,0.14201,0.20817],"object_pos_start":[0.5608,0.12271,0.27626],"object_to_goal_dist_end":0.01688,"object_to_goal_dist_start":0.06187,"object_z_max":0.27666,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54934,0.14271,0.23212],"tcp_start":[0.5457,0.12277,0.29625],"tcp_to_object_dist_end":0.02463,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37391,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12127,"approach_object.generator.speed":0.09511,"descend_grasp.grasp_z":0.00011,"descend_to_place.descend_speed":0.0519,"descend_to_place.place_z_adjust":-0.00106,"grasp_object.grasp_offset":-0.01169,"lift_object.lift_height":0.16951,"transport_to_goal.transport_speed":0.04904},"optimized_scores":{"best_composite_score":0.45367,"best_fitness_score":0.97367,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49897,0.04285,-0.00172],"force_p95":0.4938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53132,"mean_force":0.18471,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48726,0.04221,0.0374]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3321.0,"contact_point_centroid":[0.49147,0.06132,0.08933],"force_p95":0.10945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31501,"mean_force":0.0639,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49009,0.04224,0.08727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2977.0,"contact_point_centroid":[0.49154,0.02313,0.08986],"force_p95":0.11278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26853,"mean_force":0.06836,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4901,0.04224,0.08711]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.04475,-0.00224],"force_p95":0.18748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25989,"mean_force":0.13988,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4897,0.04244,0.03734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1414.0,"contact_point_centroid":[0.56025,0.24231,0.19771],"force_p95":0.14559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24363,"mean_force":0.09827,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55466,0.22352,0.19603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1675.0,"contact_point_centroid":[0.56071,0.20527,0.19702],"force_p95":0.1257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20995,"mean_force":0.08132,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55468,0.22363,0.19565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3444.0,"contact_point_centroid":[0.52825,0.10783,0.19033],"force_p95":0.10999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15852,"mean_force":0.08244,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52309,0.12637,0.18882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3184.0,"contact_point_centroid":[0.52814,0.14502,0.19086],"force_p95":0.10992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1451,"mean_force":0.08638,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5231,0.12636,0.18883]},{"body_a":"world","body_b":"grasp_target","contact_count":712.0,"contact_point_centroid":[0.50118,0.04505,-0.00182],"force_p95":0.1376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12331,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49936,0.01646,0.24172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4833.0,"contact_point_centroid":[0.48869,0.02311,0.03918],"force_p95":0.07547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13519,"mean_force":0.04452,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48857,0.04234,0.03615]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49701,0.03887,0.112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.48855,0.06175,0.03868],"force_p95":0.0764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08079,"mean_force":0.04231,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48858,0.04234,0.03616]}],"total_contact_groups":12},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5718,0.2348,0.14088],"final_tcp_position":[0.55799,0.23465,0.1614],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.4989,0.03488,0.17866],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.153,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.497,0.04305,0.04541],"tcp_start":[0.4989,0.03488,0.17866],"tcp_to_object_dist_end":0.01993,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04297,0.02519],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24402,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.48854,0.04234,0.03612],"tcp_start":[0.497,0.04305,0.04541],"tcp_to_object_dist_end":0.01669,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":178.0,"n_steps_budget":990.0,"object_pos_end":[0.51402,0.04283,0.14282],"object_pos_start":[0.50115,0.04297,0.02519],"object_to_goal_dist_end":0.20827,"object_to_goal_dist_start":0.24402,"object_z_max":0.14215,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.49594,0.04251,0.15556],"tcp_start":[0.48854,0.04234,0.03612],"tcp_to_object_dist_end":0.02212,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.56685,0.21375,0.20757],"object_pos_start":[0.51402,0.04283,0.14282],"object_to_goal_dist_end":0.06834,"object_to_goal_dist_start":0.20827,"object_z_max":0.20733,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55256,0.21368,0.22589],"tcp_start":[0.49594,0.04251,0.15556],"tcp_to_object_dist_end":0.02323,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.5718,0.2348,0.14088],"object_pos_start":[0.56685,0.21375,0.20757],"object_to_goal_dist_end":0.0138,"object_to_goal_dist_start":0.06834,"object_z_max":0.20788,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55799,0.23465,0.1614],"tcp_start":[0.55256,0.21368,0.22589],"tcp_to_object_dist_end":0.02474,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31022,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1103,"approach_object.generator.speed":0.06939,"descend_grasp.grasp_z":2e-05,"descend_to_place.descend_speed":0.05556,"descend_to_place.place_z_adjust":-0.00375,"grasp_object.grasp_offset":-0.00277,"lift_object.lift_height":0.21813,"transport_to_goal.transport_speed":0.04346},"optimized_scores":{"best_composite_score":0.45471,"best_fitness_score":0.97471,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.47424,-0.01917,-0.00154],"force_p95":0.50577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52731,"mean_force":0.19306,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46357,-0.01912,0.03817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1239.0,"contact_point_centroid":[0.61952,0.15985,0.23615],"force_p95":0.1756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4293,"mean_force":0.1172,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61396,0.14141,0.23968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.61969,0.12311,0.23676],"force_p95":0.16937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34495,"mean_force":0.10972,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61392,0.14136,0.23988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4284.0,"contact_point_centroid":[0.46792,-0.03817,0.10902],"force_p95":0.10918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27257,"mean_force":0.06464,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46631,-0.01914,0.10724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3955.0,"contact_point_centroid":[0.4678,-5e-05,0.10924],"force_p95":0.11238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26626,"mean_force":0.06834,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46629,-0.01914,0.10678]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02003,-0.00209],"force_p95":0.14794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21119,"mean_force":0.12951,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46593,-0.01917,0.03815]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3689.0,"contact_point_centroid":[0.54104,0.03341,0.23569],"force_p95":0.11124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15892,"mean_force":0.08529,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53527,0.05189,0.23427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3359.0,"contact_point_centroid":[0.54611,0.07626,0.23855],"force_p95":0.12034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15047,"mean_force":0.08933,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54042,0.05765,0.23683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5296.0,"contact_point_centroid":[0.46425,0.00011,0.03863],"force_p95":0.06626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.142,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46485,-0.01915,0.03708]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48989,-0.00737,0.23778]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47512,-0.01747,0.10759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5442.0,"contact_point_centroid":[0.46425,-0.03844,0.03851],"force_p95":0.06629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07355,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46485,-0.01915,0.03708]}],"total_contact_groups":12},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63185,0.15106,0.17705],"final_tcp_position":[0.6221,0.15118,0.20168],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47899,-0.01571,0.16964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14371,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47298,-0.01931,0.04546],"tcp_start":[0.47899,-0.01571,0.16964],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01937,0.02568],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28814,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46482,-0.01915,0.03705],"tcp_start":[0.47298,-0.01931,0.04546],"tcp_to_object_dist_end":0.016,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.49162,-0.01922,0.19058],"object_pos_start":[0.47607,-0.01937,0.02568],"object_to_goal_dist_end":0.22666,"object_to_goal_dist_start":0.28814,"object_z_max":0.18991,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47231,-0.01925,0.20465],"tcp_start":[0.46482,-0.01915,0.03705],"tcp_to_object_dist_end":0.0239,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.62246,0.13279,0.2503],"object_pos_start":[0.49162,-0.01922,0.19058],"object_to_goal_dist_end":0.06642,"object_to_goal_dist_start":0.22666,"object_z_max":0.25009,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.60808,0.13333,0.27045],"tcp_start":[0.47231,-0.01925,0.20465],"tcp_to_object_dist_end":0.02476,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.63185,0.15106,0.17705],"object_pos_start":[0.62246,0.13279,0.2503],"object_to_goal_dist_end":0.01531,"object_to_goal_dist_start":0.06642,"object_z_max":0.25047,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.6221,0.15118,0.20168],"tcp_start":[0.60808,0.13333,0.27045],"tcp_to_object_dist_end":0.02649,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```